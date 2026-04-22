"""
tests/unit/lgd_decompiler/generate_LGC/test_ast_assignment_parens.py
Test the parenthesis protection behavior of assignment statements in different contexts.

Verify that independent assignments are not contaminated and
nested assignments are correctly enclosed in parentheses.
"""

import pytest
from tests.conftest import ASM_FILES_DIR
from tests.utils.ast_helpers import parse_asm_methods, build_ast_for_method
from lgd_tool.lgd_decompiler.generate_LGC.flow_structurer import FlowStructurer

# ==========================================
# 1. Another ASM file
# ==========================================
ASM_FILE = ASM_FILES_DIR / "test_assignment_parens.lgd.asm"

# read methods
methods = parse_asm_methods(str(ASM_FILE)) if ASM_FILE.exists() else []
test_method = next((m for m in methods if m.name == "test_advanced_assignments"), None)


def generate_struct_code_for_test() -> str:
    """生成完整提取并化简后的高级代码流控制结构文本。"""
    if not test_method:
        return ""

    from lgd_tool.lgd_decompiler.generate_LGC.lgc_generator import CFGBuilder
    from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import ASTBuilder

    cfg_builder = CFGBuilder()
    ast_builder = ASTBuilder()
    blocks = cfg_builder.build_cfg(test_method)

    for i, block in enumerate(blocks):
        statements = ast_builder.build_block_ast(
            block,
            is_last_physical_block=(i == len(blocks) - 1),
            method_name=test_method.name,
        )
        block.statements = statements

    flow = FlowStructurer(blocks)
    flow.build_structure()
    region = flow.fold_into_tree()
    return region.to_code(0)


CODE_TEXT = generate_struct_code_for_test()


# ==========================================
# 2. asserts table
# ==========================================

# 这些代码片段中的赋值，本身就具有足够的独立性，必须保证它们没有受到额外括号"污染"
EXPECTED_NO_PARENS = [
    # 纯独立赋值
    "test_advanced_assignments_local0 = 100;",
    "test_advanced_assignments_local1 += test_advanced_assignments_local0;",
    "test_advanced_assignments_local2 -= test_advanced_assignments_local1;",

    # 连续赋值 (独立成句的)
    "test_advanced_assignments_local0 = test_advanced_assignments_local1 = test_advanced_assignments_local2 = 0;",

    # For 循环初始化和自增长
    "for (test_advanced_assignments_local0 = 0; (test_advanced_assignments_local0 < 20); test_advanced_assignments_local0 += 1) {",

    # 函数行内隐式传参
    "Action(0, test_advanced_assignments_local0 = 5, test_advanced_assignments_local1 += 10);"
]


# 这些代码片段中的赋值，由于处于计算节点内部（作为其左、右子嗣节点），
# 因此必须被防御性地括起来，以此保障低优先级的赋值能够先触发
EXPECTED_WITH_PARENS = [
    # While 条件中的复合赋值和关系运算嵌套 <
    "while (((test_advanced_assignments_local0 -= 1) >= 0)) {",

    # If 复合逻辑运算 (&&) + 内部关系运算 != 与 >
    "if ((((test_advanced_assignments_local0 = GetValue()) != 0) && ((test_advanced_assignments_local1 += test_advanced_assignments_local0) > 10))) {",

    # 数组下标作为左值内部，还包含复合赋值
    "test_advanced_assignments_local3[test_advanced_assignments_local0 += 1] = test_advanced_assignments_local1 -= 5;",

    # 乘除及加减混合运算
    "((test_advanced_assignments_local0 += 10) * (test_advanced_assignments_local1 -= 5))",

    # 单目操作符 (取负, 取非, 取反)
    "(-(test_advanced_assignments_local0 = 5))",
    "(!(test_advanced_assignments_local1 += 1))",
    "(~(test_advanced_assignments_local0 -= 2))",

    # 移位与位运算
    "(((test_advanced_assignments_local0 = 1) << 2) & ((test_advanced_assignments_local1 = 2) >> 1))"
]


@pytest.mark.skipif(not test_method, reason="Can't find target method in ASM file.")
def test_assignment_parens_unprotected_statements():
    """测试常规独立赋值是否没有被错误追加不需要的安全括号。"""
    for expected in EXPECTED_NO_PARENS:
        assert expected in CODE_TEXT, (
            f"未在生成的代码结构中找到期望的纯净(无括号)格式片段: \n'{expected}'"
        )


@pytest.mark.skipif(not test_method, reason="Can't find target method in ASM file.")
def test_assignment_parens_protected_statements():
    """测试嵌套至特定运算中的赋值行为是否被追加了至关重要的防御性安全括号。"""
    for expected in EXPECTED_WITH_PARENS:
        assert expected in CODE_TEXT, (
            f"未在生成的代码结构中找到期望的受保护嵌套括号格式片段: \n'{expected}'"
        )
