"""
test/test_asm/conftest.py
为 tutorial_00 测试集定义 session 级别的 fixture。
整个 test session 只运行一次 pipeline，所有测试共享结果。
测试全部结束后，等待用户按 Enter 清理生成的 .asm 文件。
"""

import os
import sys
import pytest

# 确保项目根在路径中
_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from test.test_utils import run_pipeline_to_asm, parse_asm_file, wait_and_cleanup

LGD_PATH = os.path.join(_ROOT, ".lgd_sample", "tutorial_00.lgd")


@pytest.fixture(scope="session")
def tutorial00_session(request):
    """
    Session 级别 fixture：
    - 运行 pipeline 到 ASM 生成
    - 解析生成的 ASM 文件
    - 测试结束后等用户按 Enter 清理
    返回: (ctx, asm_path, asm_functions)
    """
    ctx, asm_path = run_pipeline_to_asm(LGD_PATH)
    asm_functions = parse_asm_file(asm_path)

    def finalizer():
        wait_and_cleanup([asm_path])

    request.addfinalizer(finalizer)

    return ctx, asm_path, asm_functions
