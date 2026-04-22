"""
tests/unit/lgd_decompiler/generate_LGC/test_ast_ifdef_recovery.py
Test the recovery logic for ifdef compiler bugs during AST construction.

Verify alerts and code generation under various && / || exception truncation scenarios.
"""

import pytest
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import CommentNode

# expecting table
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
        "warnings": [],  # normal methods, should no warning
        "code_snippets": ["(test_ifdef_bug_or_start_local0 > 50)"]
    },
    "test_ifdef_bug_and_start": {
        "warnings": [],  # normal methods, should no warning
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
        "warnings": [],  # The called sub-function did not generate any warnings.
        "code_snippets": ["return 123;"]
    },
    "test_ifdef_func_arg": {
        "warnings": ["Operation '&&' unexpectedly terminated"],
        "code_snippets": ["getImplantPrice(test_ifdef_func_arg_local0) > 0"]
    }
}


def test_ast_ifdef_recover(ast_method_session):
    """
    asserts: each method and its expected warning value
    """
    method_name, statements = ast_method_session

    if method_name not in EXPECTED_RESULTS:
        pytest.fail(f"发现了未知的测试方法 {method_name}，请在 EXPECTED_RESULTS 中补充它的期望值。")

    expected = EXPECTED_RESULTS[method_name]

    # 1. Verify warning comments (Warnings)
    warnings = [s.text for s in statements if isinstance(s, CommentNode)]
    expected_warnings = expected.get("warnings", [])

    # If no warnings are expected,
    # assert that the warnings list does not contain the keyword Original compiler bug
    if not expected_warnings:
        for w in warnings:
            assert "Original compiler bug detected" not in w, (
                f"[{method_name}] 预期无告警，但实际产生了异常告警: {w}"
            )
    else:
        # If alerts are expected, ensure that all expected alerts are found in the generated comments
        for expected_warn in expected_warnings:
            assert any(expected_warn in w for w in warnings), (
                f"[{method_name}] 缺失期望的警告: '{expected_warn}'\n"
                f"实际获取到的警告: {warnings}"
            )

    # 2. Verify the generated code snippets
    code = "\n".join(s.to_code() for s in statements)

    for expected_snippet in expected.get("code_snippets", []):
        assert expected_snippet in code, (
            f"[{method_name}] 代码中未找到期望的逻辑片段: '{expected_snippet}'\n"
            f"实际生成的代码:\n{code}"
        )
