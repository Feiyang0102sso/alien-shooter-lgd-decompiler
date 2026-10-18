"""
tests/unit/lgd_decompiler/generate_LGC/test_ast_array_index_binding.py
测试 ARRAY_IDX 挂起下标的绑定：
- ADDR_OF 必须消费挂起下标，生成 &arr[i]
- 下标未被紧随其后的指令消费、被套到 __DUMMY_ARG__ 上、块尾残留，均为 error
- 提交后从未被任何调用取走的参数为 error
"""

import pytest

from lgd_tool.logger import logger, FatalError
from lgd_tool.lgd_decompiler.generate_LGC.asm_structs import AsmInstruction
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import ASTBuilder
from lgd_tool.lgd_decompiler.generate_LGC.cfg_structs import BasicBlock

METHOD_NAME = "main"


@pytest.fixture
def stop_on_error():
    """开启 stop_on_error，使 error_and_stop 抛出 FatalError，测试后恢复。"""
    logger.set_stop_on_error(True)
    yield
    logger.set_stop_on_error(False)


def _build_block(instr_specs: list) -> BasicBlock:
    """
    由 (助记符, 操作数列表) 构造单个基本块。

    :param instr_specs: 形如 [("PUSH_VAR", ["main_local4"]), ("ARRAY_IDX", [])]
    :return: BasicBlock
    """
    block = BasicBlock(id=0, start_offset=0)
    offset = 0
    for mnemonic, operands in instr_specs:
        block.instructions.append(AsmInstruction(offset=offset, mnemonic=mnemonic, operands=operands))
        offset = offset + 5
    return block


def _build_code(instr_specs: list) -> str:
    """构造基本块并生成 AST，返回拼接后的代码文本。"""
    statements = ASTBuilder().build_block_ast(_build_block(instr_specs), method_name=METHOD_NAME)
    code_lines = []
    for stmt in statements:
        code_lines.append(stmt.to_code())
    return "\n".join(code_lines)


def test_addr_of_consumes_array_index(stop_on_error) -> None:
    """
    p = &pathName[i]：ADDR_OF 消费挂起下标，下标不再跑到等号左边。
    """
    code = _build_code([
        ("PUSH_VAR", ["main_local4"]),
        ("ARRAY_IDX", []),
        ("ADDR_OF", ["main_local0"]),
        ("ASSIGN", ["main_local5"]),
    ])
    assert "main_local5 = (&main_local0[main_local4])" in code


def test_leaked_array_index_raises(stop_on_error) -> None:
    """
    ARRAY_IDX 之后的指令未消费下标（下标漂向后续变量）必须报错。
    栈保持平衡：旧逻辑会静默生成 main_local5[main_local4] = 7，不会触发 Stack_Out，只有新检查能拦住。
    """
    block = _build_block([
        ("PUSH_VAR", ["main_local4"]),
        ("ARRAY_IDX", []),
        ("PUSH_INT", ["7"]),
        ("ASSIGN", ["main_local5"]),
    ])
    with pytest.raises(FatalError):
        ASTBuilder().build_block_ast(block, method_name=METHOD_NAME)


def test_dummy_arg_with_array_index_raises(stop_on_error) -> None:
    """
    默认参数占位符 __DUMMY_ARG__ 收到下标必须报错。
    """
    block = _build_block([
        ("PUSH_VAR", ["main_local4"]),
        ("ARRAY_IDX", []),
        ("PUSH_VAR", ["Action_arg3"]),
    ])
    with pytest.raises(FatalError):
        ASTBuilder().build_block_ast(block, method_name=METHOD_NAME)


def test_unconsumed_array_index_at_block_end_raises(stop_on_error) -> None:
    """
    块结束时仍有挂起下标必须报错。
    """
    block = _build_block([
        ("PUSH_VAR", ["main_local4"]),
        ("ARRAY_IDX", []),
    ])
    with pytest.raises(FatalError):
        ASTBuilder().build_block_ast(block, method_name=METHOD_NAME)


def test_unused_fallback_argument_raises(stop_on_error) -> None:
    """
    提交后既不符合 Func_argN 命名、也没被任何调用取走的参数，会被静默丢弃，必须报错。
    """
    block = _build_block([
        ("PUSH_INT", ["1"]),
        ("ASSIGN", ["not_an_arg_name"]),
        ("ARG_COMMIT", []),
    ])
    with pytest.raises(FatalError):
        ASTBuilder().build_block_ast(block, method_name=METHOD_NAME)
