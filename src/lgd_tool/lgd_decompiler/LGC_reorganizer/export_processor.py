"""
export_processor.py

处理反编译后 LGC 文件的 extern 导出函数声明。
本文件包含了导出函数声明的拆分解析、物理文件生成、以及多文件之间的导出函数原序强一致性校验与合并功能。
"""

import sys
import re
from pathlib import Path
from lgd_tool.logger import logger

# 常量配置写在开头方便调试
# 匹配 extern 导出声明的正则模式
# 必须符合: extern stackObject(int stackObject_arg0) 100; 等标准格式
EXTERN_PATTERN = re.compile(r"^\s*extern\s+[^;]+;\s*(?://.*)?$")


def normalize_declaration_line(line: str) -> str:
    """
    对导出声明或变量声明行进行宽容归一化处理。
    去除多余的前后空格，并将中间多余的连续空白字符压缩为单个空格。

    :param line: 原始的声明行字符串
    :return: 压缩空格归一化后的声明行字符串
    """
    stripped_text = line.strip()
    words = stripped_text.split()
    clean_line = " ".join(words)
    return clean_line


def extract_extern_declarations(lgc_content: str) -> list[str]:
    """
    解析 LGC 文本内容，提取其中包含的所有 extern 导出函数声明。

    :param lgc_content: 原始 LGC 文件的全部文本内容
    :return: 包含所有 extern 声明的字符串列表（未归一化，保留原样）
    """
    lines = lgc_content.splitlines()
    extern_declarations = []

    for line in lines:
        stripped_line = line.strip()
        # 跳过空行
        if len(stripped_line) == 0:
            continue
        
        # 匹配正则模式
        match = EXTERN_PATTERN.match(line)
        if match is not None:
            extern_declarations.append(stripped_line)
            
    logger.debug("Extracted %d extern declarations", len(extern_declarations))
    return extern_declarations


def verify_exports_strictly_identical(file_to_exports: dict[str, list[str]]) -> list[str]:
    """
    对多个大文件提取出来的 export 声明执行严苛一致性校验。
    不仅校验数量，也深度校验每一条声明的字符内容及物理出现位置顺序。
    一旦检测出任何不一致，打印错误日志并安全熔断进程。

    :param file_to_exports: 大文件物理名映射到其 extern 声明列表的字典，格式为 { "file_a.lgc": [extern 声明] }
    :return: 经过归一化处理的首个非空有效基准声明行列表
    """
    # 1. 归一化所有导出声明
    file_to_clean_decls = {}
    for file_name, raw_lines in file_to_exports.items():
        clean_decls = []
        for line in raw_lines:
            if line.strip() != "":
                clean_line = normalize_declaration_line(line)
                clean_decls.append(clean_line)
        file_to_clean_decls[file_name] = clean_decls

    # 2. 寻找第一个非空的列表作为基准黄金样本进行比对
    base_file_name = None
    base_decls = []
    for file_name, clean_decls in file_to_clean_decls.items():
        if len(clean_decls) > 0:
            base_file_name = file_name
            base_decls = clean_decls
            break

    # 3. 如果所有文件的 extern 声明全部为空，则直接跳过一致性校验
    if base_file_name is None:
        logger.info("All export signatures are empty, skipping export consistency check.")
        return []

    # 4. 逐一将其他大文件的声明与黄金基准样本进行严格比对
    for other_file_name, other_decls in file_to_clean_decls.items():
        # 跳过基准文件本身
        if other_file_name == base_file_name:
            continue

        # 允许个别特殊文件全空（例如 temp.lgc）
        if len(other_decls) == 0:
            logger.debug(f"Skipped export consistency check for empty file: '{other_file_name}'")
            continue

        # 4.1 校验声明的数量是否完全相同
        if len(base_decls) != len(other_decls):
            error_message = (
                f" [Exporter Merger] The number of Export interface entries in each source file is inconsistent!\n"
                f" * Absolute base file: '{base_file_name}' contains {len(base_decls)} extern declarations\n"
                f" * Difference file detected: '{other_file_name}' contains {len(other_decls)} extern declarations"
            )
            logger.error(error_message)
            sys.exit(1)

        # 4.2 校验每行内容及物理原序是否完全对齐
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


def write_export_file(
    extern_declarations: list[str],
    output_path: Path,
    include_segments: list[str] = None,
) -> None:
    """
    将提取合并后的所有 extern 导出函数声明物理写入 core/export.lgc。
    并在文件头部及尾部引入防重定义哨兵机制（#ifndef / #define 宏）。
    若包含首段 segment_00.lgc，则会在宏哨兵结束前自动内联 include。

    :param extern_declarations: 归一化后的导出函数声明列表
    :param output_path: 目标写出物理文件 Path
    :param include_segments: 需要内联引用的普通段物理文件名列表（如 ["segment_00.lgc"]）
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 构造 ifndef 防重定义包含保护宏
    file_lines = []
    file_lines.append("#ifndef _CORE_EXPORT_LGC_")
    file_lines.append("#define _CORE_EXPORT_LGC_ aaa")
    file_lines.append("")
    file_lines.append("// ==========================================")
    file_lines.append("// Export Definitions")
    file_lines.append(f"// Total Declarations: {len(extern_declarations)}")
    file_lines.append("// ==========================================")
    file_lines.append("")

    for decl in extern_declarations:
        file_lines.append(decl)
        
    if include_segments is not None:
        if len(include_segments) > 0:
            file_lines.append("")
            file_lines.append("// ==========================================")
            file_lines.append("// Include Segment_00 Functions")
            file_lines.append("// ==========================================")
            file_lines.append("")
            for seg in sorted(include_segments):
                file_lines.append(f'#include "{seg}"')
            
    file_lines.append("")
    file_lines.append("#endif")
    file_lines.append("")
    
    content = "\n".join(file_lines)
    output_path.write_text(content, encoding="utf-8")
    logger.debug("Successfully wrote export file with include guard to: %s", output_path)
