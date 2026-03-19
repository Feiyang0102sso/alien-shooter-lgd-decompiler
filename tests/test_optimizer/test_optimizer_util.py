"""
tests/test_optimizer/test_optimizer_util.py
优化器测试专用的 helper 函数。
"""
from pathlib import Path
from lgd_tool.lgd_decompiler.generate_LGC.lgc_generator import LgcGenerator


def generate_and_read_lgc(asm_path: Path, csv_path: Path, output_lgc_path: Path) -> str:
    """
    运行完整的反编译流水线，生成 LGC 文件并读取其内容。

    Returns:
        str: 生成的 LGC 文件内容文本
    """
    LgcGenerator.generate_complete_lgc(str(asm_path), str(output_lgc_path), str(csv_path))

    if not output_lgc_path.exists():
        return ""

    return output_lgc_path.read_text(encoding="utf-8")