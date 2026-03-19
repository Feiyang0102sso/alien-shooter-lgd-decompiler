"""
LGC_refiner/refiner.py
LGC Refiner 主入口。
调度 extern 替换和常量替换两个子模块。
"""

from pathlib import Path
from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.LGC_refiner.database_loader import load_extern_database, load_constants_database
from lgd_tool.lgd_decompiler.LGC_refiner.extern_refiner import refine_externs
from lgd_tool.lgd_decompiler.LGC_refiner.const_refiner import refine_constants


class LgcRefiner:
    """
    LGC 后处理优化器。
    从指定目录加载 extern 和 constants 数据库，
    对已生成的 LGC 文本执行符号替换。
    """

    def __init__(self, data_dir: Path):
        """
        :param data_dir: 数据目录路径（包含 extern_database.json 和 constants_database.json）
        """
        extern_path = data_dir / "extern_database.json"
        const_path = data_dir / "constants_database.json"

        self.extern_db = load_extern_database(extern_path)
        self.const_db = load_constants_database(const_path)

    def refine(self, lgc_text: str) -> str:
        """
        对 LGC 文本执行全部优化。

        :param lgc_text: 原始 LGC 文本
        :return: 优化后的 LGC 文本
        """
        logger.info("[Refiner] Starting LGC refinement...")

        # 1. Extern 函数声明替换
        lgc_text = refine_externs(lgc_text, self.extern_db)

        # 2. 常量符号替换
        lgc_text = refine_constants(lgc_text, self.const_db)

        logger.info("[Refiner] LGC refinement completed")
        return lgc_text
