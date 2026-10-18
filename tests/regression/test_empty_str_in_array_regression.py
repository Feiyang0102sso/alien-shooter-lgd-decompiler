"""
tests/regression/test_empty_str_in_array_regression.py
回归测试：字符串数组初始化列表中的空串 "" 曾被反编译成 "\"\""（两个双引号字符）。
现场见 ASNE startEquipmentTemplatesInInventory：以 "" 作结尾哨兵的 while 循环永不结束，点击生存模式即卡死。

fixture 链路（用例名 empty_str_in_array）：
  original_lgc/empty_str_in_array/  源码，编译得到 ↓
  lgd_files/empty_str_in_array/     本回归的输入
"""

import shutil

import pytest

from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR, TESTS_DIR

# ===== 常量配置 =====
FIXTURE_LGD = LGD_FILES_DIR / "empty_str_in_array" / "empty_str.lgd"
WORK_DIR = TESTS_DIR / "output" / "empty_str_in_array"

# 修复后应还原出的声明（空串曾被反编译成 "\"\""）
EXPECTED_DECLARATIONS = [
    # 全局数组
    'string items[4] = { "a", "b", "c", "" };',
    # 数组参数默认值
    'string pick_arg0[2] = { "x", "" }',
    # static 局部数组
    'static string main_local0[3] = { "t1", "", "t3" };',
    # 对照组：真实的两个双引号字符必须原样保留，不能被当成空串
    'string quoted[2] = { "\\"\\"", "" };',
]


@pytest.fixture(scope="module")
def decompiled_lgc() -> str:
    """
    在独立工作目录中以 stop_on_error 模式反编译 fixture，返回 LGC 文本。
    """
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    work_lgd = WORK_DIR / FIXTURE_LGD.name
    shutil.copy2(FIXTURE_LGD, work_lgd)

    # stop_on_error 是全局状态，无论成败都必须恢复，避免影响其他测试
    logger.set_stop_on_error(True)
    try:
        LgdPipeline(str(work_lgd)).run(keep_intermediate=False)
    finally:
        logger.set_stop_on_error(False)

    content = work_lgd.with_suffix(".lgc").read_text(encoding="utf-8")

    yield content

    shutil.rmtree(WORK_DIR)


@pytest.mark.parametrize("declaration", EXPECTED_DECLARATIONS)
def test_empty_string_restored_in_array(decompiled_lgc: str, declaration: str):
    """
    三条数组路径中的空串均还原为 ""；真实的两个双引号字符原样还原为 "\\"\\""。
    """
    assert declaration in decompiled_lgc
