"""
merger.py
"""

import sys
from pathlib import Path
from lgd_tool.logger import logger


def normalize_declaration_line(line: str) -> str:
    """
    normalize declaration line

    :arg line: original line
    :return: normalized line
    """
    stripped_text = line.strip()
    words = stripped_text.split()
    clean_line = " ".join(words)
    return clean_line


def verify_exports_strictly_identical(file_to_exports: dict[str, list[str]]) -> list[str]:
    """
    exam the extern declarations, should be EXACTLY same
    including the declaration order
    if anything is not same, throw a error and stop the pipeline

    :param file_to_exports: dict, Key,name/dir for the large lgc; Value extern declarations
    :return: a list of extern that is normalized and set as the golden
    """
    # 1. normalize all
    file_to_clean_decls = {}
    for file_name, raw_lines in file_to_exports.items():
        clean_decls = []
        for line in raw_lines:
            if line.strip() != "":
                clean_line = normalize_declaration_line(line)
                clean_decls.append(clean_line)
        file_to_clean_decls[file_name] = clean_decls

    # 2. find a non-empty list as gold to compare
    base_file_name = None
    base_decls = []
    for file_name, clean_decls in file_to_clean_decls.items():
        if len(clean_decls) > 0:
            base_file_name = file_name
            base_decls = clean_decls
            break

    # 3. if all extern is empty, return empty list []
    if base_file_name is None:
        logger.info("All export signatures are empty, skipping export consistency check.")
        return []

    # 4. compare one with another
    for other_file_name, other_decls in file_to_clean_decls.items():
        # skip itself for comparing
        if other_file_name == base_file_name:
            continue

        # empty extern is allowed (such as temp.lgc)
        if len(other_decls) == 0:
            logger.info(f"Skipped export consistency check for empty file: '{other_file_name}'")
            continue

        # 4.1 check the extern nums
        if len(base_decls) != len(other_decls):
            error_message = (
                f" [Exporter Merger] The number of Export interface entries in each source file is inconsistent!\n"
                f" * Absolute base file: '{base_file_name}' contains {len(base_decls)} extern declarations\n"
                f" * Difference file detected: '{other_file_name}' contains {len(other_decls)} extern declarations"
            )
            logger.error(error_message)
            sys.exit(1)

        # 4.2 check the order and the declaration details
        total_count = len(base_decls)
        for idx in range(total_count):
            base_line_content = base_decls[idx]
            other_line_content = other_decls[idx]
            if base_line_content != other_line_content:
                error_message = (
                    f" [Exporter Merger] Export declaration detected a inconsistency on physical line {idx + 1}!\n"
                    f" either the code is from different game version or the code is damaged!\n"
                    f" * Absolute base file '{base_file_name}' is defined at this physical location:\n"
                    f" >>> {base_line_content}\n"
                    f" * Difference conflict file '{other_file_name}' is defined at this physical location:\n"
                    f" >>> {other_line_content}"
                )
                logger.error(error_message)
                sys.exit(1)

    logger.info("Successfully verified all export signatures are 100% identical in original physical order!")
    return base_decls


def extract_variable_name(declaration: str) -> str:
    """
    extract var name from normalized lines

    eg:
        "int SoundVolume;" -> "SoundVolume"
        "string musicAmbient = \"music\\\\mus00.ogg\";" -> "musicAmbient"
        "int AmmoPrice[11] = { 0 };" -> "AmmoPrice"

    :param declaration: normalized global var lines
    :return: str: global var names
    """
    clean_decl = declaration.strip()
    
    # 1. remove type prefixes
    if clean_decl.startswith("int "):
        clean_decl = clean_decl[4:].strip()
    elif clean_decl.startswith("string "):
        clean_decl = clean_decl[7:].strip()
        
    # 2. Filter the variable name fields sequentially.
    # Stop when meeting a space, square brackets, equal sign, or semicolon.
    name_chars = []
    for char in clean_decl:
        if char == " " or char == "[" or char == "=" or char == ";":
            break
        name_chars.append(char)
        
    var_name = "".join(name_chars)
    return var_name.strip()


def process_global_variables(
    file_to_globals: dict[str, list[str]],
    output_dir: Path,
) -> dict[str, list[str]]:
    """
    Merge and categorize global var from multiple large lgc to remove duplicates,
    and return a map of differences/conflicts.
    
    Rule:
        1. If everything is same, merge into core/global_variable.lgc
        2. If collision happen, it belongs to last segment (main entrance)

    :param file_to_globals: global vars mapping from big lgc, format { "tutorial_00.lgc": [global vars] }。
    :param output_dir: output dir
    :return: distinguished var that need to be injected into its own file, format { "tutorial_00.lgc": [global local vars] }。
    """
    from lgd_tool.lgd_decompiler.LGC_splitter import write_global_variable_file

    # 1. Global var format { variable name: { file name: normalized declaration } }
    var_registry = {}

    for file_name, decl_lines in file_to_globals.items():
        for line in decl_lines:
            stripped = line.strip()
            if stripped != "":
                normalized = normalize_declaration_line(stripped)
                var_name = extract_variable_name(normalized)
                
                if var_name not in var_registry:
                    var_registry[var_name] = {}
                var_registry[var_name][file_name] = normalized

    public_globals = []
    # record the var that need to be injected into each one (conflict)
    file_local_injections = {name: [] for name in file_to_globals.keys()}

    # 2. Classify and analyze each variable name.
    for var_name, occurrences in var_registry.items():
        unique_declarations = set(occurrences.values())
        
        # As long as there is no definition conflict it is all classified as global.
        if len(unique_declarations) == 1:
            public_globals.append(list(unique_declarations)[0])
        else:
            # conflicting
            # eg: int var = 100; && int var = 10;
            warning_detail = (
                f"[Global Merger] Global Var '{var_name}' have conflict or is exclusive between files\n"
                f"  -> Conflict/Exclusive distribution and details: \n"
                f"{occurrences}"
            )
            logger.warning(warning_detail)

            # Distribute and save to the private injection queue of the corresponding file
            for file_name, decl_text in occurrences.items():
                file_local_injections[file_name].append(decl_text)

    # 3. write into core/global_variable.lgc
    output_globals_file = output_dir / "core" / "global_variable.lgc"
    write_global_variable_file(public_globals, output_globals_file)

    return file_local_injections


class LgcSegmentPool:
    """
    Global segment management and deduplication merging pool.
    
    Rule:
        - each segment will assemble in memory and its MD5 hash fingerprint is calculated.
        - Use the content's MD5 hash as the key to track it in the global dictionary.
        - if same fingerprints, not write into disk and combine to a existing one
        - if meet new fingerprint, dynamically allocated (e.g., segment_01.lgc;
        if a conflict occurs, the suffix is incremented to segment_01_001.lgc),
        and the fingerprint is physically written to the disk and recorded.
    """

    def __init__(self, output_dir: Path):
        """
        init seg pool

        :param output_dir: The merged and deduplicated LGC segment written root directory.
        """
        self.output_dir = output_dir
        # 保存已注册去重的全局段，格式为 { md5_hash: 物理文件名(如 "segment_01.lgc") }
        self.pool = {}
        # 已被分配的物理文件名集合，用于防撞名冲突
        self.assigned_filenames = set()
        # 记录各大文件拆分后的普通段物理引用引用链，格式为 { "tutorial_00.lgc": ["segment_01.lgc", "segment_02.lgc"] }
        self.file_references = {}

    def register_file_segments(self, file_name: str, segments: list[list["LgcFunction"]]) -> None:
        """
        注册并合流某个大文件切分出来的普通段列表（该列表已在外部过滤掉最后一个主入口段）。
        按照普通段在原文件中的物理引用顺序，依次在内存哈希池中去重匹配，完成去重与物理文件名序列绑定。

        :param file_name: 原始大文件物理名（如 "level_01.lgc"）
        :param segments: 该文件切分出来的非主入口的普通段（Segment）列表。
        """
        import hashlib

        self.file_references[file_name] = []

        for idx, seg_funcs in enumerate(segments):
            # 1. 拼接段内所有函数的原始代码行，计算该段唯一的 MD5 哈希内容指纹
            lines_list = []
            for func in seg_funcs:
                func_text = "\n".join(func.lines)
                lines_list.append(func_text)
            
            # 使用空行隔开并拼合成整段文本
            seg_content = "\n\n".join(lines_list)
            
            # 统一换行符，防止跨平台 Windows 与 Linux 换行符的物理差异干扰指纹计算
            normalized_content = seg_content.replace("\r\n", "\n")
            seg_hash = hashlib.md5(normalized_content.encode("utf-8")).hexdigest()

            # 2. 精确研判全局段池中是否已存在完全一致的段指纹
            if seg_hash in self.pool:
                existing_filename = self.pool[seg_hash]
                
                # 100% 完全一致（差一个字节都不行）！直接将已有的文件名登记在其引用链中，完成乱序同类项合并
                self.file_references[file_name].append(existing_filename)
                
                logger.info(
                    f"[SEGMENT MATCH] 文件 '{file_name}' 第 {idx + 1} 个段内容与 "
                    f"已有物理文件 '{existing_filename}' 完全一致，成功合并同类项！"
                )
            else:
                # 3. 这是一个全新的普通段，按顺序为其分配全局文件名
                desired_name = f"segment_{len(self.pool):02d}.lgc"

                # 4. 名字冲突避让安全阀：若文件名已被其他地方抢占（防撞名），自动加后缀递增
                suffix_idx = 1
                base_stem = Path(desired_name).stem
                while desired_name in self.assigned_filenames:
                    desired_name = f"{base_stem}_{suffix_idx:03d}.lgc"
                    suffix_idx += 1

                # 5. 登记存入哈希池并记录到文件的引用链中
                self.pool[seg_hash] = desired_name
                self.assigned_filenames.add(desired_name)
                self.file_references[file_name].append(desired_name)

                # 6. 安全物理写入磁盘
                self._write_segment_to_disk(desired_name, seg_content)
                logger.info(
                    f"[SEGMENT NEW] 发现新普通代码段，成功物理写入文件: {desired_name}"
                )

    def _write_segment_to_disk(self, file_name: str, content: str) -> None:
        """
        物理落盘写入一个合并去重后的普通段文件。
        在头部自动添加对 core/export.lgc 以及 core/global_variable.lgc 的引用，
        并通过 #ifndef 哨兵机制规避因游戏引擎重复包含产生的重定义报错。

        :param file_name: 普通段物理文件名。
        :param content: 段的完整内容文本。
        """
        out_path = self.output_dir / file_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 生成唯一的防重包含 include guard 宏名，例如 segment_01.lgc -> _SEGMENT_01_LGC_
        macro_name = f"_{file_name.upper().replace('.', '_').replace('-', '_')}_"

        file_lines = []
        # 写入 ifndef 哨兵头部
        file_lines.append(f"#ifndef {macro_name}")
        file_lines.append(f"#define {macro_name} aaa")
        file_lines.append("")
        file_lines.append("// ==========================================")
        file_lines.append(f"// file {file_name}")
        file_lines.append("// ==========================================")
        file_lines.append("")

        # 针对每一个普通 segment，在其头部引用 core/export.lgc 以及 core/global_variable.lgc
        file_lines.append('#include "core\\export.lgc"')
        file_lines.append('#include "core\\global_variable.lgc"')
        file_lines.append("")

        file_lines.append(content)
        file_lines.append("")
        # 写入 ifndef 哨兵尾部
        file_lines.append("#endif")
        file_lines.append("")

        out_path.write_text("\n".join(file_lines), encoding="utf-8")


def merge_decompiled_project(
    project_data: dict[str, dict],
    output_dir: Path,
) -> dict[str, list[str]]:
    """
    一键统一执行 LGC 反编译项目的多文件合并、去重、Export 原序强校验与 Global 差异局部注入。
    该接口是整个项目合并去重流程的顶层一键协调器（Pipeline）。
    
    一键调度顺序:
        1. 提取所有大文件的 Export 数据并执行 verify_exports_strictly_identical 原序强校验，一致后物理落盘 core/export.lgc。
        2. 提取所有大文件的 Global 数据，调用 process_global_variables 对无冲突合流，冲突或独占的注入到各自大文件的主脚本头部最开头。
        3. 实例化 LgcSegmentPool 段池，遍历大文件注册普通段（非主入口段）执行哈希去重合并物理写盘，并生成解耦的有序引用链序列。
        4. 物理组装并写出各大地图主脚本入口文件（头部自动生成标准的公共与私有依赖的 #include 链，中段注入特异冲突全局变量，尾段拼入主入口代码）。

    project_data 数据格式如下:
        {
            "tutorial_00.lgc": {
                "exports": [原始 extern 声明行],
                "globals": [原始全局变量声明行],
                "segments": [[LgcFunction], [LgcFunction]],  # 普通段列表（物理已剥离最后一个主入口段）
                "last_segment_lines": [主入口原有原始代码行列表]
            },
            "tutorial_01.lgc": {
                ...
            }
        }

    :param project_data: 整个项目的内存级数据结构。
    :param output_dir: 合并物理写出的目标物理根目录。
    :return: 各大文件在合并后，解耦引用位置生成的物理有序依赖链映射字典，格式为 { "tutorial_00.lgc": ["segment_01.lgc"] }。
    """
    from lgd_tool.lgd_decompiler.LGC_splitter.export_splitter import write_export_file

    # 1. 第一阶段：提取并执行 Export 强一致原序校验，成功后准备公共 API 库
    file_to_exports = {}
    for file_name, parts in project_data.items():
        file_to_exports[file_name] = parts.get("exports", [])
    
    clean_exports = verify_exports_strictly_identical(file_to_exports)
    public_export_file = output_dir / "core" / "export.lgc"

    # 2. 第二阶段：合流全局变量。有冲突/特异的会返回在 file_local_injections 字典中
    file_to_globals = {}
    file_last_segment_lines = {}
    for file_name, parts in project_data.items():
        file_to_globals[file_name] = parts.get("globals", [])
        file_last_segment_lines[file_name] = parts.get("last_segment_lines", [])

    file_local_injections = process_global_variables(
        file_to_globals=file_to_globals,
        output_dir=output_dir
    )

    # 3. 第三阶段：普通代码段内容哈希去重与段池引用关系链生成
    pool = LgcSegmentPool(output_dir)
    for file_name, parts in project_data.items():
        file_segments = parts.get("segments", [])
        pool.register_file_segments(file_name, file_segments)

    # 【重构调整】在第三阶段注册完毕后，收集所有有关卡的第 0 份 segment 去重文件名列表并写入 core/export.lgc 末尾
    segment_0_files = set()
    for file_name, parts in project_data.items():
        export_funcs = parts.get("export_functions", [])
        if len(export_funcs) > 0:
            refs = pool.file_references.get(file_name, [])
            if len(refs) > 0:
                segment_0_files.add(refs[0])

    write_export_file(
        extern_declarations=clean_exports,
        output_path=public_export_file,
        include_segments=list(segment_0_files)
    )

    # 4. 物理拼装并落盘各大文件的主入口脚本（主地图脚本入口）
    for file_name in project_data.keys():
        main_script_path = output_dir / file_name
        
        # 确保该主入口脚本所在的子物理文件夹已被安全创建
        main_script_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 构造带有标准公共与普通非主段依赖 include 链的完整主脚本
        main_file_lines = []
        main_file_lines.append("// ==========================================")
        main_file_lines.append(f"// Entrance Map Script: {file_name}")
        main_file_lines.append("// ==========================================")
        main_file_lines.append("")
        
        # 注入基础公共头 include（统一使用项目根目录相对路径）
        main_file_lines.append('#include "core\\export.lgc"')
        main_file_lines.append('#include "core\\global_variable.lgc"')
        main_file_lines.append("")

        # 提前注入本关私有/有冲突的局部全局变量声明，
        local_decls = file_local_injections.get(file_name, [])
        if len(local_decls) > 0:
            main_file_lines.append("// ==========================================")
            main_file_lines.append("// Local/Conflict Global Variables")
            main_file_lines.append(f"// Total: {len(local_decls)} items")
            main_file_lines.append("// ==========================================")
            for decl in local_decls:
                main_file_lines.append(decl)
            main_file_lines.append("")
        
        # 注入该地图有序依赖的哈希去重后的公共普通代码段 include (剥离第 0 份段，因其已在 core/export.lgc 中前置内嵌引用)
        refs = pool.file_references[file_name]
        export_funcs = project_data[file_name].get("export_functions", [])
        
        if len(export_funcs) > 0 and len(refs) > 0:
            remaining_refs = refs[1:]
        else:
            remaining_refs = refs

        for ref_seg in remaining_refs:
            main_file_lines.append(f'#include "{ref_seg}"')
            
        main_file_lines.append("")  # 留空行
        
        # 拼接在此前第二阶段中未包含局部变量的原生末端主脚本代码
        local_main_code = file_last_segment_lines[file_name]
        for line in local_main_code:
            main_file_lines.append(line)
            
        main_file_lines.append("")
        
        # 物理写盘
        main_script_path.write_text("\n".join(main_file_lines), encoding="utf-8")
        logger.info(
            f"Successfully compiled and wrote entrance map script with dependency chain: {file_name}"
        )

    # 返回各大文件的物理有序引用关系映射
    return pool.file_references


def split_and_backup_single_file(lgd_file_path: str, output_dir: Path) -> None:
    """
    一键对单个 LGD 文件反编译生成的巨型 LGC 执行原地 .bak.lgc 物理安全备份，
    并自动拆分为 core/export、core/global 以及普通段。
    该封装极大地减轻了项目入口 main.py 的代码臃肿。

    :param lgd_file_path: 原始的 .lgd 文件路径。
    :param output_dir: 物理拆分写出的目标目录。
    """
    import shutil
    from lgd_tool.lgd_decompiler.LGC_splitter.export_splitter import (
        extract_extern_declarations,
        write_export_file,
    )
    from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import (
        extract_globals_from_content,
        write_global_variable_file,
    )
    from lgd_tool.lgd_decompiler.LGC_splitter.func_splitter import (
        parse_lgc_functions,
        decide_segments,
        write_segment_files,
    )

    lgd_p = Path(lgd_file_path)
    lgc_file_path = lgd_p.with_suffix(".lgc")

    if not lgc_file_path.exists():
        logger.error(f"[SPLITTER] Cannot find generated LGC file to split: {lgc_file_path}")
        return

    # 1. 物理备份：在原地安全地创建一个对应的 .bak.lgc 物理备份文件
    bak_path = lgc_file_path.with_suffix(".bak.lgc")
    try:
        shutil.copyfile(lgc_file_path, bak_path)
        logger.info(f"[BACKUP] Successfully created LGC backup file: {bak_path.name}")
    except Exception as e:
        logger.error(f"[BACKUP] Failed to create LGC backup file: {e}")

    # 2. 读取并拆分大文件
    logger.info(f"[SPLITTER] Running Splitter for single file: {lgd_file_path}")
    lgc_content = lgc_file_path.read_text(encoding="utf-8", errors="replace")
    
    functions = parse_lgc_functions(lgc_content)
    segments_dict = decide_segments(functions)
    export_functions = segments_dict.get("export", [])
    
    has_segment_0 = len(export_functions) > 0
    if has_segment_0:
        segments_dict["segments"].insert(0, export_functions)
        segments_dict["export"] = []
        
    # 2.1 提取并物理写入 core/export.lgc (内嵌包含 segment_00.lgc 如果存在)
    externs = extract_extern_declarations(lgc_content)
    include_segs = ["segment_00.lgc"] if has_segment_0 else None
    write_export_file(
        externs,
        output_dir / "core" / "export.lgc",
        include_segments=include_segs
    )
    
    # 2.2 提取并物理写入 core/global_variable.lgc
    globals_list = extract_globals_from_content(lgc_content)
    write_global_variable_file(globals_list, output_dir / "core" / "global_variable.lgc")
    
    # 2.3 物理切分普通段落落盘
    write_segment_files(segments_dict, output_dir, lgd_p.name)
    logger.info(f"[SPLITTER] Splitter completed successfully for: {lgd_file_path}")


def merge_and_backup_project(lgd_file_paths: list[str], output_dir: Path) -> None:
    """
    一键对批量 LGD 文件反编译生成的巨型 LGC 执行原地 .bak.lgc 物理安全备份，
    并自动提取、过滤与剥离数据，最终一键调度合并协调器执行跨文件合并去重写盘。
    该封装极大地减轻了项目入口 main.py 的代码臃肿。

    :param lgd_file_paths: 成功反编译的所有 .lgd 文件路径列表。
    :param output_dir: 物理合并去重输出的项目工程目标根目录。
    """
    import shutil
    from lgd_tool.lgd_decompiler.LGC_splitter.export_splitter import extract_extern_declarations
    from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import extract_globals_from_content
    from lgd_tool.lgd_decompiler.LGC_splitter.func_splitter import (
        parse_lgc_functions,
        decide_segments,
    )

    logger.info("\n" + "=" * 60)
    logger.info("[SPLITTER] Starting Project-level Merge & Deduplication Pipeline...")
    logger.info("=" * 60)

    project_data = {}

    for lgd_path in lgd_file_paths:
        lgd_p = Path(lgd_path)
        lgc_file_path = lgd_p.with_suffix(".lgc")

        if lgc_file_path.exists():
            # 1. 物理备份：在原地安全地创建一个对应的 .bak.lgc 物理备份文件
            bak_path = lgc_file_path.with_suffix(".bak.lgc")
            try:
                shutil.copyfile(lgc_file_path, bak_path)
                logger.info(f"[BACKUP] Successfully created LGC backup file: {bak_path.name}")
            except Exception as e:
                logger.error(f"[BACKUP] Failed to create LGC backup file: {e}")

            # 2. 读取大文件内容进行解析提取与主脚本剥离
            lgc_content = lgc_file_path.read_text(encoding="utf-8", errors="replace")

            # 2.1 提取 export API
            externs = extract_extern_declarations(lgc_content)
            # 2.2 提取 global 变量
            globals_list = extract_globals_from_content(lgc_content)
            # 2.3 提取顶层函数
            functions = parse_lgc_functions(lgc_content)
            # 2.4 切分普通段并剥离最后一个段（主入口段）
            segments_dict = decide_segments(functions)
            all_segs = segments_dict.get("segments", [])
            export_funcs = segments_dict.get("export", [])
            
            # 将第一次跳转前的 export 顶级函数作为第 0 份 segment，插入普通段的最前面
            if len(export_funcs) > 0:
                all_segs.insert(0, export_funcs)
            
            pure_segments = []
            last_segment_lines = []
            
            if len(all_segs) > 0:
                # 剥离最后一个普通段作为主脚本
                last_seg = all_segs[-1]
                pure_segments = all_segs[:-1]
                
                # 拼接原有主入口函数的原始行体
                for func in last_seg:
                    for line in func.lines:
                        last_segment_lines.append(line)
                    last_segment_lines.append("")

            # 计算该 LGC 文件相对于输出根目录的相对路径以完美保留子文件夹结构
            try:
                relative_lgc_path = lgc_file_path.relative_to(output_dir)
                key_name = str(relative_lgc_path)
            except Exception:
                # 跨目录等特殊极端边缘时降级为纯文件名
                key_name = lgc_file_path.name

            # 录入合并数据库
            project_data[key_name] = {
                "exports": externs,
                "export_functions": export_funcs,
                "globals": globals_list,
                "segments": pure_segments,
                "last_segment_lines": last_segment_lines
            }
        else:
            logger.warning(f"[SPLITTER] Expected LGC file not found: {lgc_file_path}")

    # 3. 运行顶级一键项目合并协调器
    logger.info(f"[SPLITTER] Merging LGC project files into: {output_dir}")
    try:
        merge_decompiled_project(project_data, output_dir)
        logger.info("[SPLITTER] Project-level Merge & Deduplication completed successfully!")
    except Exception as e:
        logger.error(f"[SPLITTER] Project-level Merge failed: {e}")

    print("=" * 60 + "\n")


def run_splitter_pipeline(target_path: Path, success_list: list[str] = None) -> None:
    """
    一键运行 LGC 拆分与合并 Pipeline 的最高层统一入口。
    根据输入路径自动研判执行单文件拆分或多文件合并，并在执行前在 lgc 同目录下生成原地 .bak.lgc 备份。

    :param target_path: 输入目标 Path，可为单个 .lgd 文件或其所在目录。
    :param success_list: 批量模式下成功反编译的 .lgd 文件路径列表（str 类型）。
    """
    if target_path.is_file():
        # 单文件模式
        if target_path.suffix.lower() != ".lgd":
            logger.error(f"[SPLITTER] Target file '{target_path}' is not a .lgd file.")
            return

        lgc_file_path = target_path.with_suffix(".lgc")
        if not lgc_file_path.exists():
            logger.error(f"[SPLITTER] Cannot find generated LGC file to split: {lgc_file_path}")
            return

        # 物理写出目录为同名子文件夹下
        output_dir = target_path.parent / target_path.stem
        logger.info(f"[SPLITTER] Executing single-file split for: {target_path}")
        split_and_backup_single_file(str(target_path), output_dir)

    elif target_path.is_dir():
        # 批量目录模式
        if not success_list:
            logger.warning("[SPLITTER] No successful decompiled LGD files found, skipping project-level merge.")
            return

        # 直接在输入路径目录下生成合并的工程文件
        merged_output_dir = target_path
        logger.info(f"[SPLITTER] Executing project-level merge directly into: {merged_output_dir}")
        merge_and_backup_project(success_list, merged_output_dir)
    else:
        logger.error(f"[SPLITTER] Target path does not exist: {target_path}")




