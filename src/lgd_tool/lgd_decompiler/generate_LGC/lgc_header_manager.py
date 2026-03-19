"""
generate_LGC/lgc_header_manager.py
负责管理和生成 LGC 文件的头部字符串（包含 Extern 声明和 Global 变量声明）。
"""

from typing import List


class LgcHeaderManager:
    """
    LGC 头部声明管理器类。
    用于集中存储外部函数 (Externs) 和全局变量 (Globals) 的声明，
    并最终将其格式化为标准的 C 风格代码块。
    """

    def __init__(self):
        """
        初始化管理器，创建用于存储声明字符串的空列表。
        """
        self.externs: List[str] = []
        self.globals: List[str] = []

    def add_extern(self, decl: str) -> None:
        """
        添加一条外部函数 (Extern) 声明。

        :param decl: 格式化好的 extern 声明字符串 (例如 "extern func() 1;")
        """
        self.externs.append(decl)

    def add_global(self, decl: str) -> None:
        """
        添加一条全局变量 (Global) 声明。

        :param decl: 格式化好的 global 变量声明字符串 (例如 "int g_var = 0;")
        """
        self.globals.append(decl)

    def build_header_string(self) -> str:
        """
        组装并返回最终的 Header 字符串。
        如果列表为空，则生成相应的 "No Found" 注释。

        :return: 完整的头部声明文本块
        """
        lines = ["// =========================================="]
        lines.append("// --- Extern Definitions ---")
        lines.extend(self.externs if self.externs else ["// No Externs Found"])

        lines.append("\n// --- Global Variables ---")
        lines.extend(self.globals if self.globals else ["// No Globals Found"])
        lines.append("// ==========================================\n")

        return "\n".join(lines) + "\n"