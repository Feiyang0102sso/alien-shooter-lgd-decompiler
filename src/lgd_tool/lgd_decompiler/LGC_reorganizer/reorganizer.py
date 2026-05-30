"""
reorganizer.py

反编译工程 LGC 文件分割、备份与重组管线的最高层统一协调调度模块。
本文件包含了顶级一键项目合并管线（merge_decompiled_project）、单文件备份与独立分块写盘（split_and_backup_single_file）、
项目多文件备份与去重写盘（merge_and_backup_project）以及统一的一键式调度管线主入口（run_splitter_pipeline）。
"""

import shutil
from pathlib import Path
from lgd_tool.logger import logger

# 引入下层具体的语法要素处理器
from lgd_tool.lgd_decompiler.LGC_reorganizer.export_processor import (
    extract_extern_declarations,
    verify_exports_strictly_identical,
    write_export_file,
)
from lgd_tool.lgd_decompiler.LGC_reorganizer.global_var_processor import (
    extract_globals_from_content,
    process_global_variables,
    write_global_variable_file,
)
from lgd_tool.lgd_decompiler.LGC_reorganizer.func_processor import (
    LgcSegmentPool,
    decide_segments,
    parse_lgc_functions,
    write_segment_files,
)


def merge_decompiled_project(
    project_data: dict,
    output_dir: Path,
) -> dict:
    """
    一键合并整个反编译后的项目。
    该方法是多文件合并去重逻辑在内存到物理写出之间的核心总调度器（Pipeline）。
    
    协调步骤：
        1. 提取所有输入大文件的导出声明列表，调用 verify_exports_strictly_identical 实施严苛物理原序一致性比对。
        2. 提取所有输入大文件的全局变量，调用 process_global_variables 分离无冲突公共变量与特定独占冲突变量。
        3. 实例化 LgcSegmentPool 全局内存去重合并段池，将普通代码段依次登记匹配、计算 MD5 校验和并共享去重后文件。
        4. 重新组装各大文件的游戏地图入口文件（首部前置注入 #include 公共库，中部注入特异私有冲突变量，尾部还原主入口代码）。

    :param project_data: 内存级各文件解析数据集合，其字典结构如下：
        {
            "level_01.lgc": {
                "exports": [原始 extern 声明行],
                "export_functions": [LgcFunction],         # 前置 export 函数段
                "globals": [原始全局变量声明行],
                "segments": [[LgcFunction], [LgcFunction]],  # 普通分段列表
                "last_segment_lines": [主入口代码行列表]
            }
        }
    :param output_dir: 合并完成写出到物理磁盘的目标工程根目录 Path
    :return: 每一个原始大文件所对应合并段落的引用链映射字典，格式为 { "level_01.lgc": ["segment_01.lgc"] }
    """
    # 1. 第一阶段：提取并执行 export 导出声明一致性原序物理对齐校验
    file_to_exports = {}
    for file_name, parts in project_data.items():
        file_to_exports[file_name] = parts.get("exports", [])
    
    clean_exports = verify_exports_strictly_identical(file_to_exports)
    public_export_file = output_dir / "core" / "export.lgc"

    # 2. 第二阶段：分流全局变量
    file_to_globals = {}
    file_last_segment_lines = {}
    for file_name, parts in project_data.items():
        file_to_globals[file_name] = parts.get("globals", [])
        file_last_segment_lines[file_name] = parts.get("last_segment_lines", [])

    file_local_injections = process_global_variables(
        file_to_globals=file_to_globals,
        output_dir=output_dir
    )

    # 3. 第三阶段：普通非主入口段内容哈希去重与全局池映射生成
    pool = LgcSegmentPool(output_dir)
    for file_name, parts in project_data.items():
        file_segments = parts.get("segments", [])
        pool.register_file_segments(file_name, file_segments)
        
    # 所有文件注册完毕、引用计数计算完成后，统一将去重普通段物理写出
    pool.write_all_segments()

    # 收集全部原始文件排在最前的第 0 号分段（即含有前置调用的段落）去重文件名，写入核心 core/export.lgc 的尾部
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

    # 4. 第四阶段：物理组装并在各大文件主相对位置落盘主入口引导脚本
    for file_name in project_data.keys():
        main_script_path = output_dir / file_name
        
        # 确保该主脚本所在子文件夹结构安全创建
        main_script_path.parent.mkdir(parents=True, exist_ok=True)
        
        main_file_lines = []
        main_file_lines.append("// ==========================================")
        main_file_lines.append(f"// Entrance Map Script: {file_name}")
        main_file_lines.append("// ==========================================")
        main_file_lines.append("")
        
        # 统一内联 include 相对路径的公共核心层
        main_file_lines.append('#include "core\\export.lgc"')
        main_file_lines.append('#include "core\\global_variable.lgc"')
        main_file_lines.append("")

        # 注入本关特异的或有冲突的局部全局变量声明行
        local_decls = file_local_injections.get(file_name, [])
        if len(local_decls) > 0:
            main_file_lines.append("// ==========================================")
            main_file_lines.append("// Local/Conflict Global Variables")
            main_file_lines.append(f"// Total: {len(local_decls)} items")
            main_file_lines.append("// ==========================================")
            for decl in local_decls:
                main_file_lines.append(decl)
            main_file_lines.append("")
        
        # 拼入依赖的普通代码合并段落 #include（需跳过第 0 份已包含在 export 中的段）
        refs = pool.file_references[file_name]
        export_funcs = project_data[file_name].get("export_functions", [])
        
        if len(export_funcs) > 0 and len(refs) > 0:
            remaining_refs = refs[1:]
        else:
            remaining_refs = refs

        for ref_seg in remaining_refs:
            main_file_lines.append(f'#include "{ref_seg}"')
            
        main_file_lines.append("")  # 空行
        
        # 拼接在此前第二阶段中未包含局部变量的原生末端主脚本代码
        local_main_code = file_last_segment_lines[file_name]
        for line in local_main_code:
            main_file_lines.append(line)
            
        main_file_lines.append("")
        
        # 物理物理写出
        main_script_path.write_text("\n".join(main_file_lines), encoding="utf-8")
        logger.debug(
            f"Successfully compiled and wrote entrance map script with dependency chain: {file_name}"
        )

    logger.info(
        f"[MERGER SUMMARY] Successfully merged {len(project_data)} map script entrances, "
        f"generating {len(pool.pool)} unique shared code segments."
    )

    # 返回所有文件的有序关联依赖段文件名集合，方便上游做图分析
    return pool.file_references


def split_and_backup_single_file(lgd_file_path: str, output_dir: Path) -> None:
    """
    单大文件模式一键处理器：在原大文件所在处自动建立物理 .bak.lgc 原地备份，
    解析大文件并将其分割提取为 core/export.lgc、core/global_variable.lgc 与 segment_XX.lgc。

    :param lgd_file_path: 成功反编译出的原始大 LGD/LGC 文件物理位置
    :param output_dir: 写出解耦后小模块文件的目标工程根目录 Path
    """
    lgd_p = Path(lgd_file_path)
    lgc_file_path = lgd_p.with_suffix(".lgc")

    if not lgc_file_path.exists():
        logger.error(f"[SPLITTER] Cannot find generated LGC file to split: {lgc_file_path}")
        return

    # 1. 物理备份：创建原地以 .bak.lgc 结尾的安全物理备份文件
    bak_path = lgc_file_path.with_suffix(".bak.lgc")
    try:
        shutil.copyfile(lgc_file_path, bak_path)
        logger.debug(f"[BACKUP] Successfully created LGC backup file: {bak_path.name}")
    except Exception as e:
        logger.error(f"[BACKUP] Failed to create LGC backup file: {e}")

    # 2. 读取巨型 LGC 全文文本，解析并抽离主要语法块
    logger.info(f"[SPLITTER] Running Splitter for single file: {lgd_file_path}")
    lgc_content = lgc_file_path.read_text(encoding="utf-8", errors="replace")
    
    functions = parse_lgc_functions(lgc_content)
    segments_dict = decide_segments(functions)
    export_functions = segments_dict.get("export", [])
    
    # 若存在前置调用的段落，将其作为第 0 份 segment 插入
    has_segment_0 = len(export_functions) > 0
    if has_segment_0:
        segments_dict["segments"].insert(0, export_functions)
        segments_dict["export"] = []
        
    # 2.1 物理写出导出函数核心库 core/export.lgc（如果存在 segment_0 则前置内联 include）
    externs = extract_extern_declarations(lgc_content)
    include_segs = None
    if has_segment_0:
        include_segs = ["segment_00.lgc"]
    
    write_export_file(
        externs,
        output_dir / "core" / "export.lgc",
        include_segments=include_segs
    )
    
    # 2.2 物理写出全局公共变量 core/global_variable.lgc
    globals_list = extract_globals_from_content(lgc_content)
    write_global_variable_file(globals_list, output_dir / "core" / "global_variable.lgc")
    
    # 2.3 物理写出各个切分后的普通代码分段
    write_segment_files(segments_dict, output_dir, lgd_p.name)
    
    seg_count = len(segments_dict.get("segments", []))
    logger.info(
        f"[SPLITTER SUMMARY] Completed single file split for '{lgd_p.name}'. "
        f"Created 1 backup file and generated {seg_count} code segments."
    )


def merge_and_backup_project(lgd_file_paths: list, output_dir: Path) -> None:
    """
    项目级多文件重组一键处理器：批量原地生成 .bak.lgc 备份，将大 LGC 内的数据剥离清洗归档，
    最终启动顶级项目级一键合并重组管线（merge_decompiled_project）实施哈希去重落盘。

    :param lgd_file_paths: 整个反编译工程被录入的所有源 .lgd/.lgc 大文件路径列表
    :param output_dir: 去重物理写出的目标合并工程根目录 Path
    """
    logger.info("\n" + "=" * 60)
    logger.info("[SPLITTER] Starting Project-level Merge & Deduplication Pipeline...")
    logger.info("=" * 60)

    backup_count = 0
    project_data = {}

    for lgd_path in lgd_file_paths:
        lgd_p = Path(lgd_path)
        lgc_file_path = lgd_p.with_suffix(".lgc")

        if lgc_file_path.exists():
            # 1. 物理备份：创建原地以 .bak.lgc 结尾的安全物理备份文件
            bak_path = lgc_file_path.with_suffix(".bak.lgc")
            try:
                shutil.copyfile(lgc_file_path, bak_path)
                backup_count = backup_count + 1
                logger.debug(f"[BACKUP] Successfully created LGC backup file: {bak_path.name}")
            except Exception as e:
                logger.error(f"[BACKUP] Failed to create LGC backup file: {e}")

            # 2. 读取大 LGC 全文文本，解析并抽离主要语法块
            lgc_content = lgc_file_path.read_text(encoding="utf-8", errors="replace")

            # 2.1 提取 export 接口声明
            externs = extract_extern_declarations(lgc_content)
            # 2.2 提取全局变量声明
            globals_list = extract_globals_from_content(lgc_content)
            # 2.3 扫描切分函数结构体
            functions = parse_lgc_functions(lgc_content)
            # 2.4 将函数列表根据行号回跃切分为段落，并剥离尾部主函数段落
            segments_dict = decide_segments(functions)
            all_segs = segments_dict.get("segments", [])
            export_funcs = segments_dict.get("export", [])
            
            # 若含有前置跳转函数段，作为 segment_00 插入段最前端
            if len(export_funcs) > 0:
                all_segs.insert(0, export_funcs)
            
            pure_segments = []
            last_segment_lines = []
            
            if len(all_segs) > 0:
                # 剥离最后一段作为游戏地图引导主逻辑入口
                last_seg = all_segs[-1]
                pure_segments = all_segs[:-1]
                
                # 拼接原有主函数的原始代码行
                for func in last_seg:
                    for line in func.lines:
                        last_segment_lines.append(line)
                    last_segment_lines.append("")

            # 为保持大文件被反编译前原本的地图层级目录物理结构，获取大文件相对输出目标的相对路径作为 key 键名
            try:
                relative_lgc_path = lgc_file_path.relative_to(output_dir)
                key_name = str(relative_lgc_path)
            except Exception:
                # 发生跨目录物理越界时降级直接取纯文件名
                key_name = lgc_file_path.name

            # 保存大文件提取出的全套内存级元数据
            project_data[key_name] = {
                "exports": externs,
                "export_functions": export_funcs,
                "globals": globals_list,
                "segments": pure_segments,
                "last_segment_lines": last_segment_lines
            }
        else:
            logger.warning(f"[SPLITTER] Expected LGC file not found: {lgc_file_path}")

    # 3. 执行最高层一键合并协调管线，安全落盘
    logger.info(f"[BACKUP] All {backup_count} files have successfully completed backup.")
    logger.info(f"[SPLITTER] Merging LGC project files into: {output_dir}")
    try:
        merge_decompiled_project(project_data, output_dir)
        logger.info(
            f"[SPLITTER SUMMARY] Project-level Merge completed successfully! "
            f"Created backup files for {backup_count} source files."
        )
    except Exception as e:
        logger.error(f"[SPLITTER] Project-level Merge failed: {e}")

    print("=" * 60 + "\n")


def run_splitter_pipeline(target_path: Path, success_list: list = None) -> None:
    """
    一键运行 LGC 拆分与合并 Pipeline 的最高层统一入口。
    根据输入路径类型（文件或文件夹）自动判定并进入“单大文件直接拆分”或“多大文件全局重组去重合并”。

    :param target_path: 输入目标物理 Path，可以是单个 .lgd/.lgc 文件路径，或项目目标根目录路径
    :param success_list: 批量模式下需要处理的大文件路径列表（str 组成）
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

        # 写出到大文件所在的同名独立物理文件夹中进行归档
        output_dir = target_path.parent / target_path.stem
        logger.info(f"[SPLITTER] Executing single-file split for: {target_path}")
        split_and_backup_single_file(str(target_path), output_dir)

    elif target_path.is_dir():
        # 批量目录项目合并模式
        if not success_list:
            logger.warning("[SPLITTER] No successful decompiled LGD files found, skipping project-level merge.")
            return

        merged_output_dir = target_path
        logger.info(f"[SPLITTER] Executing project-level merge directly into: {merged_output_dir}")
        merge_and_backup_project(success_list, merged_output_dir)
    else:
        logger.error(f"[SPLITTER] Target path does not exist: {target_path}")
