"""
tests/utils/regression/string_literals.py
字符串常量核对：直接从 LGD 字节码取出全部 PUSH_STR 原始字符串，
与反编译 LGC 函数体中的字符串常量（反转义后）比较。

字节码一侧不经过 ASM 渲染与解析，可作为独立基准。
"""

from collections import Counter
from pathlib import Path

from lgd_tool.lgd_decompiler.common.string_literal import QUOTED_LITERAL_RE, unescape_string
from lgd_tool.lgd_decompiler.core.parsers import (
    BytecodeParser,
    FixedTableParser,
    P1LiteralParser,
    P2SymbolParser,
)

# LGC 中函数实现区的起始标记（LgcGenerator 写出）
FUNCTION_SECTION_MARKER = "// Function Implementations"


def collect_bytecode_strings(lgd_path: Path) -> list:
    """
    按 LGD 文件布局依次跳过 P1 / P2 / Action / ScriptEvent 表，解析字节码，返回全部 PUSH_STR 原始字符串。

    :param lgd_path: LGD 文件路径
    :return: 字符串列表（按字节码顺序）
    """
    data = lgd_path.read_bytes()
    _literals, offset, _is_old_version = P1LiteralParser(data).parse(0)
    _symbols, offset = P2SymbolParser(data).parse(offset)

    table_parser = FixedTableParser(data)
    _actions, offset = table_parser.parse(offset, "Action")
    _events, offset = table_parser.parse(offset, "ScriptEvent")

    instructions, _end = BytecodeParser(data).parse(offset)

    strings = []
    for entry in instructions:
        if entry.mnemonic == "PUSH_STR":
            strings.append(entry.operands[0])
    return strings


def collect_lgc_strings(lgc_text: str) -> list:
    """
    取出 LGC 函数实现区内全部字符串常量并反转义（跳过 // 注释行）。

    :param lgc_text: 反编译得到的 LGC 文本
    :return: 原始字符串列表
    """
    marker_pos = lgc_text.find(FUNCTION_SECTION_MARKER)
    body_text = lgc_text[marker_pos:]

    strings = []
    for line in body_text.splitlines():
        if line.strip().startswith("//"):
            continue
        for match in QUOTED_LITERAL_RE.finditer(line):
            strings.append(unescape_string(match.group(1)))
    return strings


def find_missing_strings(lgd_path: Path, lgc_text: str) -> Counter:
    """
    字节码中有、但 LGC 函数体中缺失（或次数不足）的字符串。

    LGC 一侧可能多出参数默认值、static 初值等非字节码字符串，因此只检查缺失方向；
    字符串被改写时，原值必然缺失，足以发现问题。

    :return: {原始字符串: 缺失次数}，为空表示全部还原
    """
    expected = Counter(collect_bytecode_strings(lgd_path))
    actual = Counter(collect_lgc_strings(lgc_text))
    return expected - actual
