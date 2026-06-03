"""
tests/regression/test_param_array_regression.py
回归测试：验证函数参数数组的识别以及初始化的正确格式输出。
"""

from pathlib import Path
import pytest
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR


_LGD_PATH = LGD_FILES_DIR / "regression_param_array.lgd"
_ASM_PATH = Path(str(_LGD_PATH) + ".asm")
_CSV_PATH = Path(str(_LGD_PATH) + ".csv")
_C_PATH = Path(str(_LGD_PATH) + ".c")
_LGC_PATH = _LGD_PATH.with_suffix(".lgc")

_INTERMEDIATE_FILES = [_ASM_PATH, _CSV_PATH, _C_PATH, _LGC_PATH]

# 应在输出 LGC 中正确包含的特征签名片段列表
_EXPECTED_SUBSTRINGS = [
    "int test_param_array_arg0[10]",
    "string test_param_array_arg1[5]",
    "int test_param_array_arg2[3] = { 1, 2, 3 }",
    "string test_param_array_arg3[2] = { \"a\", \"b\" }"
]

# 不应在输出 LGC 中包含的错误签名片段列表（避免旧 Bug 回归）
_UNEXPECTED_SUBSTRINGS = [
    "int test_param_array_arg2[3] = [1, 2, 3]",
    "string test_param_array_arg3[2] = \"[\\\"a\\\", \\\"b\\\"]\""
]


@pytest.fixture(scope="module")
def decompiled_lgc_content():
    """
    运行完整的反编译 pipeline，读取生成的 LGC 文件内容，并执行 teardown 清理中间文件。
    """
    pipeline = LgdPipeline(str(_LGD_PATH))
    pipeline.run(keep_intermediate=True)

    if not _LGC_PATH.exists():
        pytest.fail(f"Pipeline failed to generate LGC file at: {_LGC_PATH}")

    content = _LGC_PATH.read_text(encoding="utf-8")

    yield content

    # Teardown: 清理产生的中间文件
    for path in _INTERMEDIATE_FILES:
        if path.exists():
            path.unlink()


class TestParamArrayRegression:
    """
    测试类：验证方法参数中数组及初始化数组反编译的正确性。
    """

    def test_expected_array_parameters_present(self, decompiled_lgc_content: str):
        """
        验证正确的参数声明（包括类型、数组符号与花括号初始化值）均正常存在。
        """
        for substring in _EXPECTED_SUBSTRINGS:
            assert substring in decompiled_lgc_content, (
                f"Expected parameter declaration '{substring}' not found in the decompiled LGC."
            )

    def test_unexpected_array_parameters_absent(self, decompiled_lgc_content: str):
        """
        验证错误的参数声明（例如使用方括号或错误的 JSON 转义字符串初始化）不会在 LGC 中出现。
        """
        for substring in _UNEXPECTED_SUBSTRINGS:
            assert substring not in decompiled_lgc_content, (
                f"Unexpected/incorrect parameter declaration '{substring}' found in the decompiled LGC."
            )
