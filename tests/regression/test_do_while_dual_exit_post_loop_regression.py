"""
tests/regression/test_do_while_dual_exit_post_loop_regression.py

Regression: do-while dual terminal exit → post-loop spawn lost (survive mod bug).

Input: tests/fixtures/lgd_files/regression_do_while_dual_exit_post_loop.lgd

Two independent checks on ``monstersCreationTact`` decompile:
  1. while(1) 后保留 CreateSprite / Action（post-loop 刷怪）
  2. 超次数（attemps==max）用 return，不用 break
"""

from pathlib import Path

import pytest

from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline
from tests.conftest import LGD_FILES_DIR
from tests.utils.regression.post_loop_spawn_scan import (
    TARGET_FUNCTION,
    scan_lgc_file,
    scan_post_loop_spawn,
)

_LGD_PATH = LGD_FILES_DIR / "regression_do_while_dual_exit_post_loop.lgd"

_ASM_PATH = Path(str(_LGD_PATH) + ".asm")
_CSV_PATH = Path(str(_LGD_PATH) + ".csv")
_C_PATH = Path(str(_LGD_PATH) + ".c")
_LGC_PATH = _LGD_PATH.with_suffix(".lgc")

_INTERMEDIATE_FILES = [_ASM_PATH, _CSV_PATH, _C_PATH, _LGC_PATH]

# Legacy bug A: post-loop spawn lost — while(1) 后直接 return，无 CreateSprite/Action
_LEGACY_SPAWN_LOST = (
    "monstersCreationTact(int dummy)\n"
    "{\n"
    "    while (1) {\n"
    "        (monstersCreationTact_local24++);\n"
    "        if ((monstersCreationTact_local24 == monstersCreationTact_local23)) {\n"
    "            return;\n"
    "        }\n"
    "        if ((!CanPlace(MonsterQuantity[monstersCreationTact_local9], 0, 0, 0))) {\n"
    "            break;\n"
    "        }\n"
    "    }\n"
    "    return;\n"
    "}\n"
)

# Legacy bug B: 超次数误用 break（post-loop 即便存在，语义也错）
_LEGACY_MAX_ATTEMPS_BREAK = (
    "monstersCreationTact(int dummy)\n"
    "{\n"
    "    while (1) {\n"
    "        (monstersCreationTact_local24++);\n"
    "        if ((monstersCreationTact_local24 == monstersCreationTact_local23)) {\n"
    "            break;\n"
    "        }\n"
    "        if ((!CanPlace(MonsterQuantity[monstersCreationTact_local9], 0, 0, 0))) {\n"
    "            break;\n"
    "        }\n"
    "    }\n"
    "    monstersCreationTact_local26 = CreateSprite(MonsterQuantity[monstersCreationTact_local9], 0, 0, 0);\n"
    "    Action(monstersCreationTact_local26, ACT_ATTACK, Flagman(0), 0);\n"
    "}\n"
)


@pytest.fixture(scope="module")
def decompiled_lgc_path():
    """Decompile regression LGD once; clean intermediate files after."""
    pipeline = LgdPipeline(str(_LGD_PATH))
    pipeline.run(keep_intermediate=True)

    if not _LGC_PATH.exists():
        pytest.fail("Pipeline did not produce LGC: %s" % _LGC_PATH)

    yield _LGC_PATH

    for path in _INTERMEDIATE_FILES:
        if path.exists():
            path.unlink()


@pytest.fixture(scope="module")
def spawn_scan(decompiled_lgc_path):
    """Post-loop spawn scan of decompiled monstersCreationTact."""
    return scan_lgc_file(decompiled_lgc_path, function_name=TARGET_FUNCTION)


class TestDoWhileDualExitPostLoopRegression:
    """regression_do_while_dual_exit_post_loop.lgd"""

    def test_post_loop_spawn_after_while_one(self, spawn_scan):
        """
        while(1) 找位循环结束后，必须保留 CreateSprite / Action，不能只剩 return。
        """
        assert spawn_scan.function_body, "Missing %s in decompiled LGC" % TARGET_FUNCTION
        assert spawn_scan.has_while_one, "expected while(1) in %s" % TARGET_FUNCTION
        assert spawn_scan.has_create_sprite_after_loop, (
            "CreateSprite missing after while(1) in %s" % TARGET_FUNCTION
        )
        assert spawn_scan.has_action_after_loop, (
            "Action missing after while(1) in %s" % TARGET_FUNCTION
        )
        assert not spawn_scan.has_bare_return_after_loop, (
            "legacy bug: return immediately after while(1) without post-loop spawn"
        )

    def test_max_attemps_exhausted_uses_return(self, spawn_scan):
        """
        attemps==maxAttemps（超次数仍找不到位置）必须用 return 退出函数，不能 break。
        """
        assert spawn_scan.function_body, "Missing %s in decompiled LGC" % TARGET_FUNCTION
        assert spawn_scan.has_while_one, "expected while(1) in %s" % TARGET_FUNCTION
        assert spawn_scan.max_attemps_uses_return, (
            "attemps==maxAttemps should use return inside while(1)"
        )
        assert not spawn_scan.max_attemps_uses_break, (
            "attemps==maxAttemps must not use break (legacy bug)"
        )

    def test_scanner_detects_legacy_spawn_lost(self):
        """Sanity: 扫描器识别 post-loop 刷怪丢失的旧版 snippet。"""
        result = scan_post_loop_spawn(_LEGACY_SPAWN_LOST, function_name=TARGET_FUNCTION)
        assert not result.has_create_sprite_after_loop
        assert not result.has_action_after_loop
        assert result.has_bare_return_after_loop

    def test_scanner_detects_legacy_max_attemps_break(self):
        """Sanity: 扫描器识别超次数误用 break 的旧版 snippet。"""
        result = scan_post_loop_spawn(_LEGACY_MAX_ATTEMPS_BREAK, function_name=TARGET_FUNCTION)
        assert result.has_create_sprite_after_loop
        assert result.max_attemps_uses_break
        assert not result.max_attemps_uses_return
