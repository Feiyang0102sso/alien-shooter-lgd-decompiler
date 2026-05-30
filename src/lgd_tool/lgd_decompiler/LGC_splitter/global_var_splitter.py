"""
global_var_splitter.py

split all global var
based on the start/end mark
"""

from pathlib import Path
from lgd_tool.logger import logger


GLOBAL_VAR_START_MARKER = "// --- Global Variables ---"
GLOBAL_VAR_END_MARKER = "// =========================================="


def normalize_decl_text(line: str) -> str:
    """
    trim empty spaces
    actually no need, because the decompiled code is already formatted...
    but we still leave it here...
    """
    return " ".join(line.strip().split())


def extract_globals_from_content(lgc_content: str) -> list[str]:
    """
    extract global variables from the header part
    once the format changing, it means the global var section end
    """
    lines = lgc_content.splitlines()
    results = []

    # 1. locate the global var start mark
    start_idx = 0
    for idx, line in enumerate(lines):
        if GLOBAL_VAR_START_MARKER in line:
            start_idx = idx + 1
            break

    # 2. collect each line and break when format changed or meet the end mark
    for idx in range(start_idx, len(lines)):
        line = lines[idx]
        text = line.strip()

        # skip empty line
        # actually... there should not be an empty line after decompiled
        if len(text) == 0:
            continue

        # break when meet the end mark
        if text == GLOBAL_VAR_END_MARKER:
            break

        # decide if it is the global var
        is_global_var = text.endswith(";") and (text.startswith("int ") or text.startswith("string "))

        if is_global_var:
            results.append(text)
        else:
            # break when format changed
            break

    logger.info("Extracted %d global variable lines", len(results))
    return results


def write_global_variable_file(global_decls: list[str], output_path: Path) -> None:
    """
    write into core/global_variable.lgc
    introduce #ifndef / #define sentinel

    :param global_decls: global vars length
    :param output_path: output path
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
        
    file_lines.append("")
    file_lines.append("#endif")
    file_lines.append("")
    
    content = "\n".join(file_lines)
    output_path.write_text(content, encoding="utf-8")
    logger.info("Successfully wrote global variables with include guard to: %s", output_path)
