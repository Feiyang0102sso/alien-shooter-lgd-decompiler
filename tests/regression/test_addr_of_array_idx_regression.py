"""
tests/regression/test_addr_of_array_idx_regression.py
回归测试：&arr[i] 中 ADDR_OF 曾漏消费 ARRAY_IDX 的下标，下标泄漏给后续变量。
现场见 ASTD main.lgd -> refreshEnemyPathDirections()。

fixture 链路（用例名 addr_of_array_idx）：
  original_lgc/addr_of_array_idx/  源码，编译得到 ↓
  lgd_files/addr_of_array_idx/     本回归的输入
"""

import shutil

import pytest

from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR, TESTS_DIR

# ===== 常量配置 =====
FIXTURE_DIR = LGD_FILES_DIR / "addr_of_array_idx"
WORK_DIR = TESTS_DIR / "output" / "addr_of_array_idx"
DUMMY_ARG = "__DUMMY_ARG__"

# 用例名 -> 修复后反编译输出中必须出现的语句
EXPECTED_STATEMENTS = {
    # 后面跟默认参数：曾输出 (&main_local0), __DUMMY_ARG__[main_local4]
    "addr_of": ["Action(0, 165, (&main_local0[main_local4]));"],
    # 参数全传：曾丢下标，并污染下一条语句 main_local5[main_local4]
    "addr_of_full_args": [
        "Action(0, 165, (&main_local0[main_local4]), 7, 8);",
        "main_local5 = (main_local5 + main_local4);",
    ],
    # 普通函数：曾输出 setPath(0)，第一个参数整个丢失
    "addr_of_user_func": ["setPath((&main_local0[main_local4]), 0);"],
    # 直接赋值：曾输出 main_local5[main_local4] = (&main_local0)
    "addr_of_assign": ["main_local5 = (&main_local0[main_local4]);"],
}


@pytest.fixture(scope="module")
def decompiled_lgc():
    """
    在独立工作目录中以 stop_on_error 模式反编译全部用例，任何 error 都会直接中断测试。
    返回 { 用例名: 反编译得到的 LGC 文本 }。
    """
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    contents = {}
    # stop_on_error 是全局状态，无论成败都必须恢复，避免影响其他测试
    logger.set_stop_on_error(True)
    try:
        for case_name in EXPECTED_STATEMENTS:
            work_lgd = WORK_DIR / f"{case_name}.lgd"
            shutil.copy2(FIXTURE_DIR / f"{case_name}.lgd", work_lgd)
            LgdPipeline(str(work_lgd)).run(keep_intermediate=False)
            contents[case_name] = work_lgd.with_suffix(".lgc").read_text(encoding="utf-8")
    finally:
        logger.set_stop_on_error(False)

    yield contents

    shutil.rmtree(WORK_DIR)


@pytest.mark.parametrize("case_name", list(EXPECTED_STATEMENTS.keys()))
def test_addr_of_array_element_decompiled(decompiled_lgc: dict, case_name: str):
    """
    &arr[i] 应完整还原，下标不得泄漏，输出中不得残留 __DUMMY_ARG__。
    """
    content = decompiled_lgc[case_name]

    assert DUMMY_ARG not in content, f"{case_name}: {DUMMY_ARG} left in output"
    for statement in EXPECTED_STATEMENTS[case_name]:
        assert statement in content, f"{case_name}: expected '{statement}' not found"
