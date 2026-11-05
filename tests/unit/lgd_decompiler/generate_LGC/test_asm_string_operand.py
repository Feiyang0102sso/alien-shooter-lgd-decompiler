"""
tests/unit/lgd_decompiler/generate_LGC/test_asm_string_operand.py
测试 PUSH_STR 字符串操作数的解析与 LGC 输出：
- AsmParser 把整个字符串字面量作为一个操作数，反转义为原始值（; , 连续空白都属于字符串内容）
- ASTBuilder 只转义一次，输出与源码一致的 LGC 字符串常量
- 格式错误的字符串操作数报 error
"""

import pytest

from lgd_tool.logger import logger, FatalError
from lgd_tool.lgd_decompiler.generate_LGC.asm_parser import AsmParser
from lgd_tool.lgd_decompiler.generate_LGC.asm_structs import AsmInstruction
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import ASTBuilder
from lgd_tool.lgd_decompiler.generate_LGC.cfg_structs import BasicBlock

# ASM 中的字符串操作数文本 -> 解析后的原始值 -> LGC 中的字符串常量
STRING_CASES = [
    ('"gamma;missionName;map;"', "gamma;missionName;map;", '"gamma;missionName;map;"'),
    ('";"', ";", '";"'),
    ('""', "", '""'),
    ('",  perkId: "', ",  perkId: ", '",  perkId: "'),
    ('"  isMultiplayer =   "', "  isMultiplayer =   ", '"  isMultiplayer =   "'),
    ('"{\\"a\\": 1, \\"b\\": 2}"', '{"a": 1, "b": 2}', '"{\\"a\\": 1, \\"b\\": 2}"'),
    ('"x\\";\\"y"', 'x";"y', '"x\\";\\"y"'),
    ('"maps\\\\level.map"', "maps\\level.map", '"maps\\\\level.map"'),
    ('"line1\\nline2"', "line1\nline2", '"line1\\nline2"'),
]


@pytest.fixture
def stop_on_error():
    """开启 stop_on_error，使 error_and_stop 抛出 FatalError，测试后恢复。"""
    logger.set_stop_on_error(True)
    yield
    logger.set_stop_on_error(False)


def _write_asm(tmp_path, operand_text: str):
    """写出只含一条 PUSH_STR + RET 的最小 ASM 文件，返回路径。"""
    lines = [
        ";Function main() Begin",
        f"  0000:  02 41 00           PUSH_STR     {operand_text}",
        "  0003:  1F                 RET                              ; mark end of function",
        ";Function main() End",
    ]
    asm_path = tmp_path / "string_operand.asm"
    asm_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return asm_path


@pytest.mark.parametrize("operand_text,raw_value,lgc_literal", STRING_CASES)
def test_parser_keeps_whole_string_operand(tmp_path, stop_on_error, operand_text, raw_value, lgc_literal):
    """字符串字面量整体作为一个操作数，反转义为原始值。"""
    methods = AsmParser().parse_file(str(_write_asm(tmp_path, operand_text)))

    push_str = methods[0].instructions[0]
    assert push_str.mnemonic == "PUSH_STR"
    assert push_str.operands == [raw_value]


@pytest.mark.parametrize("operand_text,raw_value,lgc_literal", STRING_CASES)
def test_ast_builder_escapes_once(stop_on_error, operand_text, raw_value, lgc_literal):
    """ASTBuilder 对原始值只转义一次，得到与源码一致的 LGC 字符串常量。"""
    block = BasicBlock(id=0, start_offset=0)
    block.instructions.append(AsmInstruction(offset=0, mnemonic="PUSH_STR", operands=[raw_value]))
    block.instructions.append(AsmInstruction(offset=5, mnemonic="ASSIGN", operands=["main_local0"]))

    statements = ASTBuilder().build_block_ast(block, method_name="main")

    assert statements[0].to_code() == f"main_local0 = {lgc_literal};"


@pytest.mark.parametrize("operand_text", ['"unterminated', '"a" junk', '"bad \\x41 escape"'])
def test_malformed_string_operand_is_error(tmp_path, stop_on_error, operand_text):
    """缺少闭合引号、引号后有多余内容、不支持的转义，都必须报 error。"""
    with pytest.raises(FatalError):
        AsmParser().parse_file(str(_write_asm(tmp_path, operand_text)))
