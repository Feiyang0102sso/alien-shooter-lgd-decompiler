# test/test_ast/test_ast_ifdef_recovery.py
import pytest
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import CommentNode

# 动态期望表：配置每个方法需要检查的 Warning 和 AST 生成的代码特征
EXPECTED_RESULTS = {
    "test_ifdef_bug_and_end": {
        "warnings": ["Operation '&&' unexpectedly terminated"],
        "code_snippets": ["(test_ifdef_bug_and_end_local0 > 100)"]
    },
    "test_ifdef_bug_or_end": {
        "warnings": ["Operation '||' unexpectedly terminated"],
        "code_snippets": ["(test_ifdef_bug_or_end_local0 > 100)"]
    },
    "test_ifdef_bug_or_start": {
        "warnings": [],  # 正常的方法，不应该有告警
        "code_snippets": ["(test_ifdef_bug_or_start_local0 > 50)"]
    },
    "test_ifdef_bug_and_start": {
        "warnings": [],  # 正常的方法，不应该有告警
        "code_snippets": ["(test_ifdef_bug_and_start_local0 > 50)"]
    },
    "test_ifdef_bug_complex": {
        "warnings": ["Operation '&&' unexpectedly terminated"],
        "code_snippets": ["((test_ifdef_bug_complex_local0 == 1) || (test_ifdef_bug_complex_local1 == 2))"]
    },
    "test_ifdef_double_dangling": {
        "warnings": [
            "Operation '&&' unexpectedly terminated",
            "Operation '||' unexpectedly terminated"
        ],
        "code_snippets": ["(test_ifdef_double_dangling_local0 > 0)"]
    },
    "getImplantPrice": {
        "warnings": [],  # 被调用的子函数，没有告警
        "code_snippets": ["return 123;"]
    },
    "test_ifdef_func_arg": {
        "warnings": ["Operation '&&' unexpectedly terminated"],
        "code_snippets": ["getImplantPrice(test_ifdef_func_arg_local0) > 0"]
    }
}


def test_ast_ifdef_recover(ast_method_session):
    """
    动态校验：根据当前 fixture 传入的方法，自动断言其告警和生成的代码是否符合预期。
    """
    method_name, statements = ast_method_session

    if method_name not in EXPECTED_RESULTS:
        pytest.fail(f"发现了未知的测试方法 {method_name}，请在 EXPECTED_RESULTS 中补充它的期望值。")

    expected = EXPECTED_RESULTS[method_name]

    # 1. 校验警告注释 (Warnings)
    warnings = [s.text for s in statements if isinstance(s, CommentNode)]
    expected_warnings = expected.get("warnings", [])

    # 如果期望没有告警，断言 warnings 列表里不包含 Original compiler bug 关键字
    if not expected_warnings:
        for w in warnings:
            assert "Original compiler bug detected" not in w, (
                f"[{method_name}] 预期无告警，但实际产生了异常告警: {w}"
            )
    else:
        # 如果期望有告警，确保所有期望的告警都在生成的注释里找到了
        for expected_warn in expected_warnings:
            assert any(expected_warn in w for w in warnings), (
                f"[{method_name}] 缺失期望的警告: '{expected_warn}'\n"
                f"实际获取到的警告: {warnings}"
            )

    # 2. 校验生成的代码片段 (Code Snippets)
    code = "\n".join(s.to_code() for s in statements)

    for expected_snippet in expected.get("code_snippets", []):
        assert expected_snippet in code, (
            f"[{method_name}] 代码中未找到期望的逻辑片段: '{expected_snippet}'\n"
            f"实际生成的代码:\n{code}"
        )