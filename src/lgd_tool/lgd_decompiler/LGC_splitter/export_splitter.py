"""
export_splitter.py

split all extern funcs (export.lgc)
and write first segment into export.lgc
"""

import re
from pathlib import Path
from lgd_tool.logger import logger

# must follow: extern stackObject(int stackObject_arg0) 100;
#               extern  name      (xxx)                 int ;
EXTERN_PATTERN = re.compile(r"^\s*extern\s+[^;]+;\s*(?://.*)?$")


def extract_extern_declarations(lgc_content: str) -> list[str]:
    """
    rad & extract extern declarations

    :param
        lgc_content: contents lines of the lgc file

    :return
        a list contains all extern declarations
    """
    lines = lgc_content.splitlines()
    extern_declarations = []

    for line in lines:
        stripped_line = line.strip()
        # skip empty line
        if len(stripped_line) == 0:
            continue
        
        # match extern
        match = EXTERN_PATTERN.match(line)
        if match is not None:
            extern_declarations.append(stripped_line)
            
    logger.info("Extracted %d extern declarations", len(extern_declarations))
    return extern_declarations


def write_export_file(
    extern_declarations: list[str],
    output_path: Path,
    include_segments: list[str] = None,
) -> None:
    """
    write all extern func into core/export.lgc
    introduce #ifndef / #define sentinel
    included segment 00 before #endif

    :param
        extern_declarations: extern func produced by extract_extern_declarations()
        output_path: path for export.lgc
        include_segments: included segments name
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # add macro sentinel ifndef
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
        
    if include_segments and len(include_segments) > 0:
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
    logger.info("Successfully wrote export file with include guard to: %s", output_path)
