"""
global_var_splitter.py

LGC 全局变量提取与拆分工具。
专门用于识别、提取并保存 LGC 源码中的全局变量声明。
直接利用全局变量段连续分布在开头的物理特征进行极简扫描提取。
"""

from pathlib import Path
from lgd_tool.logger import logger


GLOBAL_VAR_START_MARKER = "// --- Global Variables ---"
GLOBAL_VAR_END_MARKER = "// =========================================="


def normalize_decl_text(line: str) -> str:
    """
    对变量声明行进行宽容归一化处理，压缩多余空白，以便在后续片断冲突校验时直接按行进行等于比对。
    """
    return " ".join(line.strip().split())


def extract_globals_from_content(lgc_content: str) -> list[str]:
    """
    从 LGC 源码文本中提取所有的全局变量声明行。
    全局变量是一整段连续固定在文件开头部分，一旦该段结束，后面就不会再有全局变量。
    """
    lines = lgc_content.splitlines()
    results = []

    # 1. 定位全局变量段的起始位置
    start_idx = 0
    for idx, line in enumerate(lines):
        if GLOBAL_VAR_START_MARKER in line:
            start_idx = idx + 1
            break

    # 2. 从起始位置开始连续收集变量，遇到首个非空且非变量定义行，或遇到终止线时立刻跳出
    for idx in range(start_idx, len(lines)):
        line = lines[idx]
        text = line.strip()

        # 跳过空行
        if len(text) == 0:
            continue

        # 如果遇到显式的全局变量块终止分隔线，直接跳出
        if text == GLOBAL_VAR_END_MARKER:
            break

        # 判断该非空行是否为合法的全局变量声明
        is_global_var = text.endswith(";") and (text.startswith("int ") or text.startswith("string "))

        if is_global_var:
            results.append(text)
        else:
            # 遇到任何非空且非全局变量定义的行，说明全局变量段物理上已彻底结束，立刻跳出
            break

    logger.info("Extracted %d global variable lines", len(results))
    return results


def write_global_variable_file(global_decls: list[str], output_path: Path) -> None:
    """
    将公共的无冲突全局变量写入 core/global_variable.lgc 文件中。
    使用 #ifndef / #define 哨兵机制，规避多重引入时的变量重定义问题。

    参数:
        global_decls: 要写入公共库的全局变量声明字符串列表。
        output_path: 输出 global_variable.lgc 的绝对路径。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_lines = []
    file_lines.append("#ifndef _CORE_GLOBAL_VARIABLE_LGC_")
    file_lines.append("#define _CORE_GLOBAL_VARIABLE_LGC_ aaa")
    file_lines.append("")
    file_lines.append(GLOBAL_VAR_END_MARKER)
    file_lines.append("// Public Global Variables")
    file_lines.append(f"// Total Variables: {len(global_decls)}")
    file_lines.append(GLOBAL_VAR_END_MARKER)
    file_lines.append("")
    
    for decl in global_decls:
        file_lines.append(decl)
        
    file_lines.append("")  # 尾部空行
    file_lines.append("#endif")
    file_lines.append("")
    
    content = "\n".join(file_lines)
    output_path.write_text(content, encoding="utf-8")
    logger.info("Successfully wrote global variables with include guard to: %s", output_path)
