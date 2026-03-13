"""
test/test_asm/conftest.py
为 tutorial_00 测试集定义 session 级别的 fixture。
整个 test session 只运行一次 pipeline，所有测试共享结果。
测试全部结束后，等待用户按 Enter 清理生成的 .asm 文件。
"""

import pytest
from pathlib import Path


from tests.test_utils import wait_and_cleanup
from tests.test_asm.test_asm_util import run_pipeline_to_asm, parse_asm_file

# datas
ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
LGD_FILES = list(DATA_DIR.glob("*.lgd"))
LGD_NAMES = [p.name for p in LGD_FILES]


@pytest.fixture(scope="session", params=LGD_FILES, ids=LGD_NAMES)
def lgd_session(request):
    """
    这个 fixture 会自动为每一个 .lgd 文件运行一次！
    如果有 3 个文件，它就会为你生成 3 份独立的数据。
    """
    # 拿到当前正在处理的那个 .lgd 文件的路径
    current_lgd_path = request.param

    # Setup
    ctx, asm_path = run_pipeline_to_asm(str(current_lgd_path))
    asm_functions = parse_asm_file(asm_path)

    # 交给测试用例
    yield ctx, asm_path, asm_functions, current_lgd_path.name

    # Teardown / Finalizer
    wait_and_cleanup([asm_path])
