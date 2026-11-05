"""
tests/unit/lgd_decompiler/common/test_string_literal.py
测试字符串字面量的转义 / 反转义（ASM 与 LGC 共用，规则与 lgc_compiler 一致）。
"""

import pytest

from lgd_tool.lgd_decompiler.common.string_literal import escape_string, unescape_string

BACKSLASH = "\\"

# 原始字符串 -> 期望的转义文本
ESCAPE_CASES = [
    ("plain", "plain"),
    ("", ""),
    ("a;b,c  d", "a;b,c  d"),
    ('say "hi"', 'say \\"hi\\"'),
    ("maps" + BACKSLASH + "level.map", "maps\\\\level.map"),
    ("line1\nline2\r\tend", "line1\\nline2\\r\\tend"),
    # 非 ASCII 字符原样保留（lgc_compiler 不支持 \xNN）
    ("quality_\xf1ommon", "quality_\xf1ommon"),
]


@pytest.mark.parametrize("raw_value,escaped_value", ESCAPE_CASES)
def test_escape_string(raw_value: str, escaped_value: str):
    """原始字符串按 \\ \" \\n \\r \\t 五种规则转义。"""
    assert escape_string(raw_value) == escaped_value


@pytest.mark.parametrize("raw_value,escaped_value", ESCAPE_CASES)
def test_unescape_is_inverse(raw_value: str, escaped_value: str):
    """反转义是转义的逆运算。"""
    assert unescape_string(escaped_value) == raw_value


@pytest.mark.parametrize("bad_value", ["a\\xb", "a\\0", "trailing\\"])
def test_unescape_rejects_unknown_escape(bad_value: str):
    """不支持的转义与末尾孤立的反斜杠直接报错，不做猜测。"""
    with pytest.raises(ValueError):
        unescape_string(bad_value)
