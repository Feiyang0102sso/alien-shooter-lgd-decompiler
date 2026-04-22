"""
tests/utils/lgc_helpers.py
LGC helper functions for test generation.
"""

from pathlib import Path
from lgd_tool.lgd_decompiler.generate_LGC.lgc_generator import LgcGenerator


def generate_and_read_lgc(asm_path: Path, csv_path: Path, output_lgc_path: Path) -> str:
    """
    Run the pipeline generate LGC and read its contents

    Returns:
        str: Text content of the generated LGC file
    """
    LgcGenerator.generate_complete_lgc(str(asm_path), str(output_lgc_path), str(csv_path))

    if not output_lgc_path.exists():
        return ""

    return output_lgc_path.read_text(encoding="utf-8")
