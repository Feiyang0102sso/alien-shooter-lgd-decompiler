"""
LGC_refiner/const_refiner.py
在特定 extern 函数调用的指定参数位置，将数字常量替换为符号名。
支持「纯常量」和「常量 + 表达式」两种情况。
"""

import re
from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.LGC_refiner.const_rules import EXPORT_CONST_REFINER_RULES


def refine_constants(lgc_text: str, const_db: dict) -> str:
    """
    根据 const_rules 中定义的函数-参数位置规则，
    在 LGC 文本中将数字常量替换为符号名。

    :param lgc_text: 原始 LGC 文本
    :param const_db: {prefix_group: {int_value: const_name}}
    :return: 替换后的 LGC 文本
    """
    if not const_db:
        return lgc_text

    total_replacements = 0

    for func_name, param_rules in EXPORT_CONST_REFINER_RULES.items():
        # 找到所有 func_name(args) 的调用，包括语句和表达式中的
        # 使用非贪婪匹配并处理嵌套括号
        call_pattern = re.compile(
            rf'\b{re.escape(func_name)}\s*\(',
        )

        new_text_parts = []
        search_start = 0

        for match in call_pattern.finditer(lgc_text):
            # 找到调用起点，提取完整的参数列表
            call_start = match.start()
            paren_start = match.end() - 1  # '(' 的位置
            paren_end = _find_matching_paren(lgc_text, paren_start)

            if paren_end is None:
                continue

            # 保留调用前的文本
            new_text_parts.append(lgc_text[search_start:call_start])

            # 提取参数列表字符串（不含外层括号）
            args_str = lgc_text[paren_start + 1:paren_end]

            # 按顶层逗号拆分参数
            args = _split_args(args_str)

            # 对注册的参数位置执行替换
            modified = False
            for param_idx, prefix_groups in param_rules.items():
                if param_idx >= len(args):
                    continue

                original_arg = args[param_idx]
                new_arg = _try_replace_const_in_arg(original_arg, prefix_groups, const_db)
                if new_arg != original_arg:
                    args[param_idx] = new_arg
                    modified = True
                    total_replacements += 1

            # 重组调用
            new_args_str = ", ".join(a.strip() for a in args)
            new_text_parts.append(f"{func_name}({new_args_str})")
            search_start = paren_end + 1

        if new_text_parts:
            new_text_parts.append(lgc_text[search_start:])
            lgc_text = "".join(new_text_parts)

    if total_replacements > 0:
        logger.info(f"[Refiner] Constant refinement: {total_replacements} replacements made")
    else:
        logger.info("[Refiner] Constant refinement: no replacements made")

    return lgc_text


def _try_replace_const_in_arg(arg_str: str, prefix_groups: list, const_db: dict) -> str:
    """
    尝试在单个参数字符串中替换数字常量。

    处理两种情况:
    1. 纯常量: "0x13" → "ACT_DESTROY_UNIT"
    2. 常量 + 表达式: "(0x100 + func_local3)" → "(GETSPRITE_VID_FLAG + func_local3)"

    :param arg_str: 参数字符串（可能含括号和运算符）
    :param prefix_groups: 该参数位置对应的前缀组列表，如 ["ACT", "ANI", "act"]
    :param const_db: 常量数据库
    """
    arg_stripped = arg_str.strip()

    # 收集所有候选前缀组的 value→name 映射
    lookup = {}
    for group in prefix_groups:
        group_data = const_db.get(group, {})
        lookup.update(group_data)

    if not lookup:
        return arg_str

    # 尝试纯常量匹配（整个参数就是一个数字）
    int_val = _try_parse_int(arg_stripped)
    if int_val is not None and int_val in lookup:
        return arg_str.replace(arg_stripped, lookup[int_val])

    # 尝试在表达式中替换数字字面量
    # 匹配十六进制数 0xABC 或十进制数（不匹配变量名中的数字）
    num_pattern = re.compile(r'\b(0x[0-9A-Fa-f]+|-?\d+)\b')

    def replace_num(m):
        num_str = m.group(1)
        val = _try_parse_int(num_str)
        if val is not None and val in lookup:
            return lookup[val]
        return num_str

    result = num_pattern.sub(replace_num, arg_str)
    return result


def _find_matching_paren(text: str, start: int) -> int | None:
    """
    从 start 位置的 '(' 开始，找到匹配的 ')' 位置。
    处理嵌套括号和字符串内的括号。
    """
    depth = 0
    in_string = False
    string_char = None
    i = start

    while i < len(text):
        ch = text[i]

        if in_string:
            if ch == '\\' and i + 1 < len(text):
                i += 2  # 跳过转义字符
                continue
            if ch == string_char:
                in_string = False
        else:
            if ch == '"':
                in_string = True
                string_char = ch
            elif ch == '(':
                depth += 1
            elif ch == ')':
                depth -= 1
                if depth == 0:
                    return i

        i += 1

    return None


def _split_args(args_str: str) -> list:
    """
    按顶层逗号拆分参数列表，正确处理嵌套括号和字符串。
    """
    args = []
    depth = 0
    in_string = False
    current = []

    i = 0
    while i < len(args_str):
        ch = args_str[i]

        if in_string:
            current.append(ch)
            if ch == '\\' and i + 1 < len(args_str):
                current.append(args_str[i + 1])
                i += 2
                continue
            if ch == '"':
                in_string = False
        else:
            if ch == '"':
                in_string = True
                current.append(ch)
            elif ch == '(':
                depth += 1
                current.append(ch)
            elif ch == ')':
                depth -= 1
                current.append(ch)
            elif ch == ',' and depth == 0:
                args.append("".join(current))
                current = []
            else:
                current.append(ch)

        i += 1

    # 最后一个参数
    remaining = "".join(current)
    if remaining.strip():
        args.append(remaining)

    return args


def _try_parse_int(s: str) -> int | None:
    """
    尝试将字符串解析为整数。
    支持十进制和十六进制。
    """
    s = s.strip()
    if not s:
        return None

    if s.startswith("0x") or s.startswith("0X"):
        try:
            return int(s, 16)
        except ValueError:
            return None

    # 去掉括号
    if s.startswith("(") and s.endswith(")"):
        s = s[1:-1].strip()

    if s.lstrip('-').isdigit():
        return int(s)

    return None
