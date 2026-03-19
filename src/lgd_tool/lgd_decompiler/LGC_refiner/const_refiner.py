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

    对于嵌套调用（如 Action(..., Action(...), ...)），
    在处理外层参数列表之前先递归处理内层，确保所有层级均被替换。

    :param lgc_text: 原始 LGC 文本
    :param const_db: {prefix_group: {int_value: const_name}}
    :return: 替换后的 LGC 文本
    """
    if not const_db:
        return lgc_text

    total_replacements = [0]  # 用 list 使内层函数能修改外层计数

    def _refine_pass(text: str) -> str:
        """对 text 做单次全函数扫描替换，遇到 args_str 先递归处理"""
        for func_name, param_rules in EXPORT_CONST_REFINER_RULES.items():
            call_pattern = re.compile(rf'\b{re.escape(func_name)}\s*\(')
            new_parts = []
            search_start = 0

            for match in call_pattern.finditer(text):
                call_start = match.start()

                # 跳过已被上一次外层处理覆盖的区域
                if call_start < search_start:
                    continue

                paren_start = match.end() - 1
                paren_end = _find_matching_paren(text, paren_start)
                if paren_end is None:
                    continue

                new_parts.append(text[search_start:call_start])

                # 先递归处理 args_str 内部的嵌套调用
                args_str = text[paren_start + 1:paren_end]
                args_str = _refine_pass(args_str)

                # 再按参数位置替换当前层的常量
                args = _split_args(args_str)
                for param_idx, prefix_groups in param_rules.items():
                    if param_idx >= len(args):
                        continue
                    original_arg = args[param_idx]
                    new_arg = _try_replace_const_in_arg(original_arg, prefix_groups, const_db)
                    if new_arg != original_arg:
                        args[param_idx] = new_arg
                        total_replacements[0] += 1

                new_args_str = ", ".join(a.strip() for a in args)
                new_parts.append(f"{func_name}({new_args_str})")
                search_start = paren_end + 1

            if new_parts:
                new_parts.append(text[search_start:])
                text = "".join(new_parts)

        return text

    lgc_text = _refine_pass(lgc_text)

    if total_replacements[0] > 0:
        logger.info(f"[Refiner] Constant refinement: {total_replacements[0]} replacements made")
    else:
        logger.info("[Refiner] Constant refinement: no replacements made")

    # 打印未优化的常量（如果有）
    _report_unoptimized_constants(lgc_text)

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
    if int_val is not None:
        if int_val in lookup:
            return arg_str.replace(arg_stripped, lookup[int_val])
        # 如果没直接匹配上，尝试用常量叠加进行分解
        decomp = _decompose_constant(int_val, lookup)
        if decomp:
            return arg_str.replace(arg_stripped, decomp)

    # 尝试在表达式中替换数字字面量
    # 匹配十六进制数 0xABC 或十进制数（不匹配变量名中的数字）
    num_pattern = re.compile(r'\b(0x[0-9A-Fa-f]+|-?\d+)\b')

    def replace_num(m):
        num_str = m.group(1)
        val = _try_parse_int(num_str)
        if val is not None:
            if val in lookup:
                return lookup[val]
            # 对于表达式中独立的常量也可以尝试分解
            decomp = _decompose_constant(val, lookup)
            if decomp:
                if " + " in decomp:
                    return f"({decomp})"
                return decomp
        return num_str

    result = num_pattern.sub(replace_num, arg_str)
    return result


def _decompose_constant(target_val: int, lookup: dict, max_depth: int = 4) -> str | None:
    """
    使用迭代加深 DFS 尝试将目标值分解为不超过 max_depth 个常量的和。
    常用于像 ENV_EARTHQUAKE + ENV_STOP 这样被编译成一个大数字的场景。
    """
    if target_val <= 0:
        return None
        
    # 只选择大于 0 且小于等于 target_val 的常量，按从大到小排序以尽早匹配大数字
    items = sorted([(v, n) for v, n in lookup.items() if 0 < v <= target_val], key=lambda x: x[0], reverse=True)
    if not items:
        return None
        
    def dfs(idx, curr_sum, depth_left, path):
        if curr_sum == target_val:
            return path
        if depth_left == 0 or idx >= len(items):
            return None
            
        # 尝试包含当前元素
        val, name = items[idx]
        if curr_sum + val <= target_val:
            res = dfs(idx + 1, curr_sum + val, depth_left - 1, path + [name])
            if res:
                return res
                
        # 不包含，继续下一个元素
        return dfs(idx + 1, curr_sum, depth_left, path)

    # 迭代加深，优先寻找最短组合
    for d in range(1, max_depth + 1):
        res = dfs(0, 0, d, [])
        if res:
            return " + ".join(res)
            
    return None


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


def _report_unoptimized_constants(lgc_text: str):
    """
    检查并打印 LGC 文本中仍未被优化的数字常量（INFO 级别）。
    """
    issues = []
    lines = lgc_text.split('\n')
    
    for line_idx, line in enumerate(lines):
        line_stripped = line.strip()
        # 跳过注释行
        if line_stripped.startswith("//"):
            continue

        for func_name, param_rules in EXPORT_CONST_REFINER_RULES.items():
            call_pattern = re.compile(rf'\b{re.escape(func_name)}\s*\(')
            for match in call_pattern.finditer(line):
                call_start = match.start()
                paren_start = line.find('(', call_start)
                if paren_start == -1:
                    continue
                
                paren_end = _find_matching_paren(line, paren_start)
                if paren_end is None:
                    continue
                
                args_str = line[paren_start + 1:paren_end]
                args = _split_args(args_str)
                
                for param_idx in param_rules.keys():
                    if param_idx < len(args):
                        arg_val = args[param_idx].strip()
                        if _is_pure_numeric_expression(arg_val):
                            issues.append((line_idx + 1, func_name, line_stripped, param_idx, arg_val))
    
    if issues:
        logger.info(f"[Refiner] Found {len(issues)} unoptimized constants:")
        for line_num, func, line_text, p_idx, arg_val in issues:
            logger.info(f"  Line {line_num}: [{func} arg {p_idx}] '{arg_val}' -> {line_text}")


def _is_pure_numeric_expression(val: str) -> bool:
    """
    判断一个参数字符串是否依然是纯数字表达式（未被符号化）。
    """
    # 移除非数字符号和纯算术连接符
    # 允许空格、括号、加减乘除、十六进制 x
    if not re.match(r'^[\s\(\)\+\-\*/0-9a-fA-FxX]+$', val):
        return False
        
    # 进一步检查确保它不是一个已经替换过的常量（虽然正则已经排除了大部分字母）
    # 但要排除掉变量名等。
    # 如果经过正则清理后还含有字母（除了 x/X 和 A-F），则它可能含有变量名。
    cleaned = re.sub(r'0[xX][0-9a-fA-F]+', '', val) # 移除十六进制数
    cleaned = re.sub(r'[0-9\s\(\)\+\-\*/]', '', cleaned) # 移除数字和符号
    
    # 如果还剩下字母，说明有变量名或已替换的常量名
    if re.search(r'[a-zA-Z_]', cleaned):
        return False
        
    return True
