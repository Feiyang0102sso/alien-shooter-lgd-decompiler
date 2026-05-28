"""
export_splitter.py

LGC export 提取与拆分工具。
专门用于识别、提取并保存 LGC 源码中的 `extern` 引擎内置函数声明。
"""

import re
from pathlib import Path
from lgd_tool.logger import logger

# 匹配 extern 语句的正则表达式，以 `extern ` 开始且以分号结尾（可能带有默认参数和尾部数字 ID）
# 例如: extern stackObject(int stackObject_arg0) 100;
# 注: 对缩进和空白字符做宽容匹配
EXTERN_PATTERN = re.compile(r"^\s*extern\s+[^;]+;\s*(?://.*)?$")


def extract_extern_declarations(lgc_content: str) -> list[str]:
    """
    从 LGC 源码文本中提取所有的 extern 声明行。

    参数:
        lgc_content: 包含 LGC 源码的完整文本字符串。

    返回:
        一个包含所有提取出的 extern 声明行（去除首尾空白）的列表。
    """
    lines = lgc_content.splitlines()
    extern_declarations = []

    for line in lines:
        stripped_line = line.strip()
        # 跳过空行
        if len(stripped_line) == 0:
            continue
        
        # 匹配 extern 声明行
        match = EXTERN_PATTERN.match(line)
        if match is not None:
            extern_declarations.append(stripped_line)
            
    logger.info("Extracted %d extern declarations", len(extern_declarations))
    return extern_declarations


def write_export_file(extern_declarations: list[str], output_path: Path) -> None:
    """
    将提取出的 extern 声明写入指定的 core/export.lgc 目标文件中。

    参数:
        extern_declarations: extern 声明行列表。
        output_path: 目标 export.lgc 文件的绝对路径。
    """
    # 确保父目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 按照文档标准，头部添加注释说明
    file_lines = []
    file_lines.append("// ==========================================")
    file_lines.append("// Export Definitions")
    file_lines.append(f"// Total Declarations: {len(extern_declarations)}")
    file_lines.append("// ==========================================")
    file_lines.append("")
    
    for decl in extern_declarations:
        file_lines.append(decl)
        
    file_lines.append("")  # 尾部留空行
    
    content = "\n".join(file_lines)
    output_path.write_text(content, encoding="utf-8")
    logger.info("Successfully wrote export file to: %s", output_path)
