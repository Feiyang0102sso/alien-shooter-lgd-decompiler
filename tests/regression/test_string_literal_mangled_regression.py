"""
tests/regression/test_string_literal_mangled_regression.py
回归测试：函数体内的字符串常量曾被 asm_parser 按通用操作数切分，
在 ';' 处截断、',' 变空格、连续空白被压缩、换行 round-trip 成字面量 \n。
现场见 ASW 7.3.4 main.lgd -> setMultiplayerData()：大厅 payload 键列表被截成 "\"gamma"，联网匹配失败。

fixture 链路（用例名 string_literal_mangled）：
  original_lgc/string_literal_mangled/  源码，编译得到 ↓
  lgd_files/string_literal_mangled/     本回归的输入
"""

import shutil

import pytest

from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR, TESTS_DIR
from tests.utils.regression.string_literals import collect_bytecode_strings, find_missing_strings

# ===== 常量配置 =====
FIXTURE_DIR = LGD_FILES_DIR / "string_literal_mangled"
WORK_DIR = TESTS_DIR / "output" / "string_literal_mangled"

# 用例名 -> 修复后反编译输出中必须出现的语句（与 original_lgc 源码逐字对应）
EXPECTED_STATEMENTS = {
    "string_literal": [
        # ';' 分隔的键列表：曾被截成 "\"gamma"
        'main_local0 = "gamma;missionName;gameMode;mode;map;level;";',
        # 单独的分隔符：曾变成空串
        'main_local0 = (main_local0 + ";");',
        # 以 ';' 结尾的前缀：曾变成 "\"message_type"
        'Log(("message_type;" + main_local0));',
        # 逗号 + 两个空格：曾变成 " perkId: "
        'Log((",  perkId: " + main_local0));',
        # JSON 中的逗号：曾被吃掉
        'Log("{\\"a\\": 1, \\"b\\": 2}");',
        # 首尾与中间的连续空白：曾被压缩成单个空格
        'Log("  isMultiplayer =   ");',
        # 引号内带 ';'：曾被截成 "x"
        'Log("x\\";\\"y");',
    ],
    "string_newline": [
        # 真实换行：曾 round-trip 成反斜杠 + n 两个字符
        'Log("line1\\nline2");',
    ],
}


@pytest.fixture(scope="module")
def decompiled_lgc():
    """
    在独立工作目录中以 stop_on_error 模式反编译全部用例，任何 error 都会直接中断测试。
    返回 { 用例名: (工作目录中的 LGD 路径, 反编译得到的 LGC 文本) }。
    """
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    results = {}
    # stop_on_error 是全局状态，无论成败都必须恢复，避免影响其他测试
    logger.set_stop_on_error(True)
    try:
        for case_name in EXPECTED_STATEMENTS:
            work_lgd = WORK_DIR / f"{case_name}.lgd"
            shutil.copy2(FIXTURE_DIR / f"{case_name}.lgd", work_lgd)
            LgdPipeline(str(work_lgd)).run(keep_intermediate=False)
            content = work_lgd.with_suffix(".lgc").read_text(encoding="utf-8")
            results[case_name] = (work_lgd, content)
    finally:
        logger.set_stop_on_error(False)

    yield results

    shutil.rmtree(WORK_DIR)


@pytest.mark.parametrize("case_name", list(EXPECTED_STATEMENTS.keys()))
def test_string_literals_decompiled_verbatim(decompiled_lgc: dict, case_name: str):
    """
    字符串常量按源码原样还原（含 ; , 连续空白、引号与换行转义）。
    """
    _work_lgd, content = decompiled_lgc[case_name]
    for statement in EXPECTED_STATEMENTS[case_name]:
        assert statement in content, f"{case_name}: expected '{statement}' not found"


@pytest.mark.parametrize("case_name", list(EXPECTED_STATEMENTS.keys()))
def test_every_bytecode_string_restored(decompiled_lgc: dict, case_name: str):
    """
    以字节码为基准：每条 PUSH_STR 的原始字符串都必须出现在 LGC 函数体中（反转义后逐字相等）。
    """
    work_lgd, content = decompiled_lgc[case_name]
    assert collect_bytecode_strings(work_lgd), f"{case_name}: fixture has no PUSH_STR"

    missing = find_missing_strings(work_lgd, content)
    assert not missing, f"{case_name}: bytecode strings missing from LGC: {dict(missing)}"
