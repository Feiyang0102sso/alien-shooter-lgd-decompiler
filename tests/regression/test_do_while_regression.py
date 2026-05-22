"""
tests/regression/test_do_while_regression.py

do-while / while 结构化质量回归：
  - 输入：tests/fixtures/lgd_files/regression_do_while.lgd
  - 判定：对反编译生成的 LGC 做 while 扫描（tests/utils/regression/while_issues_scan.py）
  - 不依赖任何金样 .lgc 文件，期望轮廓由下方常量定义
"""

from pathlib import Path

import pytest

from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR
from tests.utils.regression.while_issues_scan import (
    count_error_issues,
    count_issues_by_type,
    find_while_one_without_break,
    scan_lgc_file,
)

# 目标 LGD
_LGD_PATH = LGD_FILES_DIR / "regression_do_while.lgd"

# 流水线产物
_ASM_PATH = Path(str(_LGD_PATH) + ".asm")
_CSV_PATH = Path(str(_LGD_PATH) + ".csv")
_C_PATH = Path(str(_LGD_PATH) + ".c")
_LGC_PATH = _LGD_PATH.with_suffix(".lgc")

_INTERMEDIATE_FILES = [_ASM_PATH, _CSV_PATH, _C_PATH, _LGC_PATH]

# 期望 while 轮廓：3 个 while(1)+break，1 个合法空 while(func)，无 empty_while ERROR
_EXPECTED_WHILE_ONE = 3
_EXPECTED_EMPTY_WHILE_FUNC = 1
_EXPECTED_EMPTY_WHILE_ERROR = 0

_TARGET_FUNCTIONS = (
    "SurviveGameTact",
    "createMissionIcon",
    "moveEnemyToPosition",
    "setMarketIndexedParameter",
)


def _assert_do_while_profile(issues) -> None:
    """断言 while 扫描结果符合 do-while 回归期望轮廓。"""
    counts = count_issues_by_type(issues)
    errors = count_error_issues(issues)

    assert errors == _EXPECTED_EMPTY_WHILE_ERROR, (
        "expected 0 ERROR while issues, got %d: %s" % (errors, issues)
    )
    assert counts.get("while(1)", 0) == _EXPECTED_WHILE_ONE, (
        "expected %d while(1), got %s" % (_EXPECTED_WHILE_ONE, counts)
    )
    assert counts.get("empty_while_func", 0) == _EXPECTED_EMPTY_WHILE_FUNC, (
        "expected %d empty_while_func, got %s"
        % (_EXPECTED_EMPTY_WHILE_FUNC, counts)
    )
    assert counts.get("empty_while", 0) == 0, (
        "unexpected empty_while ERROR: %s" % counts
    )


@pytest.fixture(scope="module")
def decompiled_lgc_path():
    """
    对 regression_do_while.lgd 跑完整 LgdPipeline，返回生成的 .lgc 路径。

    结束后清理 lgd 旁所有中间产物。
    """
    pipeline = LgdPipeline(str(_LGD_PATH))
    pipeline.run(keep_intermediate=True)

    if not _LGC_PATH.exists():
        pytest.fail("Pipeline did not produce LGC: %s" % _LGC_PATH)

    yield _LGC_PATH

    for path in _INTERMEDIATE_FILES:
        if path.exists():
            path.unlink()


@pytest.fixture(scope="module")
def decompiled_while_issues(decompiled_lgc_path):
    """反编译 LGC 的 while 扫描结果。"""
    return scan_lgc_file(decompiled_lgc_path)


class TestDoWhileRegression:
    """regression_do_while.lgd 反编译结果的 while 结构化质量。"""

    def test_while_scan_profile(self, decompiled_while_issues):
        """生成 LGC 的 while 扫描结果应符合期望轮廓。"""
        _assert_do_while_profile(decompiled_while_issues)

    def test_while_one_has_break(self, decompiled_lgc_path):
        """三个 while(1) 体内均应有 break（do-while 结构化标志）。"""
        missing = find_while_one_without_break(decompiled_lgc_path)
        assert missing == [], (
            "while(1) without break in: %s" % ", ".join(missing)
        )

    def test_target_functions_present(self, decompiled_lgc_path):
        """四个目标函数均应出现在输出中。"""
        text = decompiled_lgc_path.read_text(encoding="utf-8")
        for name in _TARGET_FUNCTIONS:
            assert ("%s(" % name) in text, "Missing function %s in LGC" % name

    def test_no_legacy_empty_while_bug(self, decompiled_lgc_path):
        """不应出现旧版反编译错误：带条件但体为空的 while。"""
        text = decompiled_lgc_path.read_text(encoding="utf-8")
        assert "while ((SurviveGameTact_local5 == 0))" not in text
        assert (
            "while ((!createMissionIcon_local24) && "
            "(createMissionIcon_local23 < createMissionIcon_local22))"
        ) not in text
        assert (
            "while (CanPlace(moveEnemyToPosition_local3, moveEnemyToPosition_local1, moveEnemyToPosition_local2, moveEnemyToPosition_arg3) "
            "&& (moveEnemyToPosition_local4 < 10))"
        ) not in text
