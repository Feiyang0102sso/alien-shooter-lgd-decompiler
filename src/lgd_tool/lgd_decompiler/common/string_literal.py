r"""
common/string_literal.py
字符串字面量的转义与反转义。

ASM 与 LGC 共用同一套规则，与 lgc_compiler 实际支持的转义一致：
  \\  \"  \n  \r  \t
lgc_compiler 不接受 \xNN、\0、\' 等其它转义，其余字符（含非 ASCII 字节）原样写出。
"""

import re

# 原始字符 -> 转义写法
CHAR_TO_ESCAPE = {
    '\\': '\\\\',
    '"': '\\"',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}

# 反斜杠后的字符 -> 原始字符
ESCAPE_TO_CHAR = {
    '\\': '\\',
    '"': '"',
    'n': '\n',
    'r': '\r',
    't': '\t',
}

# 一个双引号字符串字面量；group(1) 为引号内的转义文本
QUOTED_LITERAL_PATTERN = r'"((?:[^"\\]|\\.)*)"'
QUOTED_LITERAL_RE = re.compile(QUOTED_LITERAL_PATTERN)


def escape_string(raw_value: str) -> str:
    """
    把原始字符串转义为可放进双引号的文本（不含两侧引号）。

    :param raw_value: 字节码中的原始字符串
    :return: 转义后的文本
    """
    parts = []
    for ch in raw_value:
        if ch in CHAR_TO_ESCAPE:
            parts.append(CHAR_TO_ESCAPE[ch])
        else:
            parts.append(ch)
    return "".join(parts)


def unescape_string(escaped_value: str) -> str:
    """
    escape_string 的逆运算。遇到不支持的转义直接抛 ValueError，不做猜测。

    :param escaped_value: 引号内的转义文本（不含两侧引号）
    :return: 原始字符串
    """
    result = []
    index = 0
    while index < len(escaped_value):
        ch = escaped_value[index]
        if ch != '\\':
            result.append(ch)
            index = index + 1
            continue

        if index + 1 >= len(escaped_value):
            raise ValueError(f"Dangling backslash at end of string literal: {escaped_value!r}")

        escape_char = escaped_value[index + 1]
        if escape_char not in ESCAPE_TO_CHAR:
            raise ValueError(f"Unsupported escape '\\{escape_char}' in string literal: {escaped_value!r}")

        result.append(ESCAPE_TO_CHAR[escape_char])
        index = index + 2
    return "".join(result)
