"""
LGC_refiner/lgc_refiner.py
refine all the generated code
"""
import re


class LgcRefiner:
    def __init__(self):
        # 匹配形如 (&VariableName) 或 (&Array[index]) 的模式
        # 提取出里面的变量部分
        self.re_redundant_ampersand = re.compile(r'\(\s*&([a-zA-Z0-9_\[\]]+)\s*\)')

    def refine_code(self, raw_code: str) -> str:
        """
        执行所有的后处理优化规则，按顺序提纯代码
        """
        refined_code = raw_code

        # 剥离取地址符的多余括号 (&var) -> &var
        refined_code = self._remove_ampersand_brackets(refined_code)


        return refined_code

    def _remove_ampersand_brackets(self, code: str) -> str:
        """
        将 (&Variable) 替换为 &Variable
        """
        return self.re_redundant_ampersand.sub(r'&\1', code)