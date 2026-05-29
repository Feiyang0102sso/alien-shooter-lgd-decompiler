"""
merger.py

用于合并与比对多个大 LGC 文件拆分产物的合并去重核心模块。
第一阶段：重点实现对各文件的 Export（extern 声明）进行绝对物理行顺序的严格比对与熔断合并。
"""

import sys
from pathlib import Path
from lgd_tool.logger import logger


def normalize_declaration_line(line: str) -> str:
    """
    对提取出来的声明行进行基础的去白归一化处理。
    去除首尾空白，并将多余的连续内部空格压缩为一个空格，确保比对不受无意义的排版空格干扰。

    :param line: 原始声明代码行
    :return: 归一化后的干净字符串
    """
    stripped_text = line.strip()
    words = stripped_text.split()
    clean_line = " ".join(words)
    return clean_line


def verify_exports_strictly_identical(file_to_exports: dict[str, list[str]]) -> list[str]:
    """
    100% 严苛地按照原始物理行顺序校验所有文件的 Export 声明是否完全一致。
    允许部分文件的 extern 声明完全为空（即含有 0 个 extern 声明，表示该地图无 extern 逻辑），
    但凡是声明不为空的文件，其声明的条目数量、行内容和物理顺序必须 100% 完全相同。

    若检测到任何不为空的声明与基准声明有行数不对等、内容不吻合或顺序错乱：
        1. 使用 logger.error 打印出具体的行冲突差异细节。
        2. 绕过一切其他错误过滤设置，直接调用 sys.exit(1) 强制退出整个进程实现硬熔断。

    :param file_to_exports: 字典格式，Key 为大文件绝对路径或名字，Value 为该文件提取出的原始 extern 声明行列表。
    :return: 经过归一化清洗后的非空基准 Export 声明行列表（如均为空则返回空列表 []）。
    """
    # 1. 对所有文件提取的原始声明进行归一化清洗
    file_to_clean_decls = {}
    for file_name, raw_lines in file_to_exports.items():
        clean_decls = []
        for line in raw_lines:
            if line.strip() != "":
                clean_line = normalize_declaration_line(line)
                clean_decls.append(clean_line)
        file_to_clean_decls[file_name] = clean_decls

    # 2. 寻找第一个非空的声明列表作为我们的绝对比对基准
    base_file_name = None
    base_decls = []
    for file_name, clean_decls in file_to_clean_decls.items():
        if len(clean_decls) > 0:
            base_file_name = file_name
            base_decls = clean_decls
            break

    # 3. 如果所有文件的声明都为空，不需要进行任何一致性比对，直接返回空列表 []
    if base_file_name is None:
        logger.info("All export signatures are empty, skipping export consistency check.")
        return []

    # 4. 依次对比其他所有文件的 Export
    for other_file_name, other_decls in file_to_clean_decls.items():
        # 跳过基准文件自身的对比
        if other_file_name == base_file_name:
            continue

        # 允许某些文件的声明为空（不包含任何 extern 声明）
        if len(other_decls) == 0:
            logger.info(f"Skipped export consistency check for empty file: '{other_file_name}'")
            continue

        # 4.1 优先验证两个文件的 extern 声明总条目数量是否相等
        if len(base_decls) != len(other_decls):
            error_message = (
                f" [Exporter Merger] The number of Export interface entries in each source file is inconsistent!\n"
                f" * Absolute base file: '{base_file_name}' contains {len(base_decls)} extern declarations\n"
                f" * Difference file detected: '{other_file_name}' contains {len(other_decls)} extern declarations"
            )
            logger.error(error_message)
            sys.exit(1)

        # 4.2 严格按照物理出现顺序，逐行精确对比内容
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
    从归一化后的全局变量声明字符串中提取其纯变量名称。
    用于后续冲突分类与特定主入口头部注入。

    例如:
        "int SoundVolume;" -> "SoundVolume"
        "string musicAmbient = \"music\\\\mus00.ogg\";" -> "musicAmbient"
        "int AmmoPrice[11] = { 0 };" -> "AmmoPrice"

    :param declaration: 归一化后的全局变量定义文本。
    :return: 提取出的纯变量名称字符串。
    """
    clean_decl = declaration.strip()
    
    # 1. 剥除已知的类型前缀
    if clean_decl.startswith("int "):
        clean_decl = clean_decl[4:].strip()
    elif clean_decl.startswith("string "):
        clean_decl = clean_decl[7:].strip()
        
    # 2. 依次过滤出变量名字段。遇到空格、中括号、等号或分号时立即终止
    name_chars = []
    for char in clean_decl:
        if char == " " or char == "[" or char == "=" or char == ";":
            break
        name_chars.append(char)
        
    var_name = "".join(name_chars)
    return var_name.strip()


def process_global_variables(
    file_to_globals: dict[str, list[str]],
    file_last_segment_lines: dict[str, list[str]],
    output_dir: Path,
) -> dict[str, list[str]]:
    """
    对多个源大文件的全局变量进行合并、分类去重并向主脚本头部注入。
    
    分类规则:
        1. 公共全局变量: 在所有大文件中都有声明且定义完全一致。合入 core/global_variable.lgc 文件。
        2. 差异/冲突全局变量: 在不同文件中声明不一致，或仅被部分大文件独占。
           - 不写入公共全局变量文件。
           - 使用 logger.warning 提醒用户注意该变量的物理定义冲突详情。
           - 直接注入分发到对应大文件拆分出的最后一个段脚本（即主入口脚本）的代码头部。

    :param file_to_globals: 各大文件提取出来的原始全局变量行映射，格式为 { "tutorial_00.lgc": [原始变量行] }。
    :param file_last_segment_lines: 各大文件拆分出的最后一个段物理代码行映射，格式为 { "tutorial_00.lgc": [代码行] }。
    :param output_dir: 物理输出的 LGC 根目录。
    :return: 注入了局部差异全局变量后的、最新主入口脚本代码行映射。
    """
    from lgd_tool.lgd_decompiler.LGC_splitter import write_global_variable_file

    # 1. 全局变量注册，结构为: { 变量名: { 文件名: 归一化声明 } }
    var_registry = {}
    total_files = len(file_to_globals)

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
    # 记录各大文件需要本地注入的差异/独占全局变量声明
    file_local_injections = {name: [] for name in file_to_globals.keys()}

    # 2. 对每个变量名进行分类研判
    for var_name, occurrences in var_registry.items():
        unique_declarations = set(occurrences.values())
        
        # 只要没有发生定义冲突（即该变量名对应的不同声明只有 1 种），就一律归于公共 global
        if len(unique_declarations) == 1:
            public_globals.append(list(unique_declarations)[0])
        else:
            # 存在定义冲突（即同名但在不同关卡赋值不同或类型不同），输出明确的 warning 日志提醒用户注意
            warning_detail = (
                f"[Global Merger] Global Var '{var_name}' have conflicting between files\n"
                f"  -> Specific conflict distribution and details: \n"
                f"{occurrences}"
            )
            logger.warning(warning_detail)

            # 分发保存到对应文件的私有注入队列
            for file_name, decl_text in occurrences.items():
                file_local_injections[file_name].append(decl_text)


    # 3. 物理写入 core/global_variable.lgc 公共文件
    output_globals_file = output_dir / "core" / "global_variable.lgc"
    write_global_variable_file(public_globals, output_globals_file)

    # 4. 执行对各大文件最后一个段（主入口）的物理头部注入
    updated_last_segment_lines = {}
    for file_name, original_lines in file_last_segment_lines.items():
        local_decls = file_local_injections.get(file_name, [])
        
        if len(local_decls) > 0:
            # 构造要注入的干净代码行
            injected_header = []
            injected_header.append("// ==========================================")
            injected_header.append("// Local/Conflict Global Variables (Injected Entrance Definitions)")
            injected_header.append(f"// Total: {len(local_decls)} items")
            injected_header.append("// ==========================================")
            for decl in local_decls:
                injected_header.append(decl)
            injected_header.append("")  # 留空行

            # 拼接到原主脚本入口代码的最开头
            new_lines = injected_header + original_lines
            updated_last_segment_lines[file_name] = new_lines
            logger.info(
                f"Successfully injected {len(local_decls)} conflict/local variables into "
                f"the entrance segment of: {file_name}"
            )
        else:
            updated_last_segment_lines[file_name] = original_lines

    return updated_last_segment_lines


class LgcSegmentPool:
    """
    全局 LGC 普通代码段（Segment）管理与去重合并池。
    
    核心原理:
        - 针对各大文件拆分出来的每一个普通函数段（一组 LgcFunction），在内存中完整拼接并计算其 MD5 哈希指纹。
        - 用内容 MD5 作为 Key，在全局字典中追踪它。
        - 遇到完全相同的指纹，直接抛弃物理写盘，物理上复用已有的文件名，解耦不同文件的载入/引用物理顺序。
        - 遇到全新指纹，动态分配一个未被占用的文件名（如 segment_01.lgc，遇冲突则递增后缀为 segment_01_001.lgc），物理写盘并记录。
    """

    def __init__(self, output_dir: Path):
        """
        初始化段管理池。

        :param output_dir: 合并去重后的 LGC 子物理文件物理写入根目录。
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
                desired_name = f"segment_{len(self.pool) + 1:02d}.lgc"

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
        """
        out_path = self.output_dir / file_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        file_lines = []
        file_lines.append("// ==========================================")
        file_lines.append(f"// file {file_name}")
        file_lines.append("// ==========================================")
        file_lines.append("")
        file_lines.append(content)
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

    # 1. 第一阶段：提取并执行 Export 强一致原序校验，成功后物理落盘公共 API 库
    file_to_exports = {}
    for file_name, parts in project_data.items():
        file_to_exports[file_name] = parts.get("exports", [])
    
    clean_exports = verify_exports_strictly_identical(file_to_exports)
    public_export_file = output_dir / "core" / "export.lgc"
    write_export_file(clean_exports, public_export_file)

    # 2. 第二阶段：合流全局变量。有冲突/特异的在内存中注入到 last_segment_lines 头部
    file_to_globals = {}
    file_last_segment_lines = {}
    for file_name, parts in project_data.items():
        file_to_globals[file_name] = parts.get("globals", [])
        file_last_segment_lines[file_name] = parts.get("last_segment_lines", [])

    updated_last_segments = process_global_variables(
        file_to_globals=file_to_globals,
        file_last_segment_lines=file_last_segment_lines,
        output_dir=output_dir
    )

    # 3. 第三阶段：普通代码段内容哈希去重与段池引用关系链生成
    pool = LgcSegmentPool(output_dir)
    for file_name, parts in project_data.items():
        file_segments = parts.get("segments", [])
        pool.register_file_segments(file_name, file_segments)

    # 4. 物理拼装并落盘各大文件的主入口脚本（主地图脚本入口）
    for file_name in project_data.keys():
        main_script_path = output_dir / file_name
        
        # 确保该主入口脚本所在的子物理文件夹已被安全创建
        main_script_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 动态计算当前大文件相对于输出根目录的反向相对路径层级前缀
        rel_p = Path(file_name)
        depth = len(rel_p.parent.parts)
        path_prefix = ""
        for _ in range(depth):
            path_prefix += "..\\"
            
        # 构造带有标准公共与普通非主段依赖 include 链的完整主脚本
        main_file_lines = []
        main_file_lines.append("// ==========================================")
        main_file_lines.append(f"// Entrance Map Script: {file_name}")
        main_file_lines.append("// ==========================================")
        main_file_lines.append("")
        
        # 注入基础公共头 include（相对路径）
        main_file_lines.append(f'#include "{path_prefix}core\\export.lgc"')
        main_file_lines.append(f'#include "{path_prefix}core\\global_variable.lgc"')
        
        # 注入该地图有序依赖的哈希去重后的公共普通代码段 include
        for ref_seg in pool.file_references[file_name]:
            main_file_lines.append(f'#include "{path_prefix}{ref_seg}"')
            
        main_file_lines.append("")  # 留空行
        
        # 拼接在此前第二阶段中被注入了特异冲突变量的末端主脚本代码
        local_main_code = updated_last_segments[file_name]
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
    
    # 2.1 提取并物理写入 core/export.lgc
    externs = extract_extern_declarations(lgc_content)
    write_export_file(externs, output_dir / "core" / "export.lgc")
    
    # 2.2 提取并物理写入 core/global_variable.lgc
    globals_list = extract_globals_from_content(lgc_content)
    write_global_variable_file(globals_list, output_dir / "core" / "global_variable.lgc")
    
    # 2.3 物理切分普通段落落盘
    functions = parse_lgc_functions(lgc_content)
    segments_dict = decide_segments(functions)
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




