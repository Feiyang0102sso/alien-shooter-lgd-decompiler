"""
tests/unit/lgd_decompiler/common/test_old_version_flag.py
测试旧版 LGD 文件的完整反编译流程。

使用 test_old_version_flag.lgd 跑完 LgdPipeline 全流程，
验证旧版 flag（0xC1/0xC2 等）能被正确识别为 string/int，
而非回退到 unknown_int。
"""

import pytest
from pathlib import Path

from tests.conftest import LGD_FILES_DIR
from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline


# 目标 LGD 文件
_LGD_PATH = LGD_FILES_DIR / "test_old_version_flag.lgd"

# 流水线产物路径
_ASM_PATH = Path(str(_LGD_PATH) + ".asm")
_CSV_PATH = Path(str(_LGD_PATH) + ".csv")
_C_PATH = Path(str(_LGD_PATH) + ".c")
_LGC_PATH = _LGD_PATH.with_suffix(".lgc")

# 需要清理的中间文件列表
_INTERMEDIATE_FILES = [_ASM_PATH, _CSV_PATH, _C_PATH, _LGC_PATH]


@pytest.fixture(scope="module")
def lgc_content():
    """
    运行完整 LgdPipeline 并返回生成的 LGC 文本。

    流水线结束后自动清理所有中间产物。
    """
    pipeline = LgdPipeline(str(_LGD_PATH))
    pipeline.run(keep_intermediate=True)

    content = _LGC_PATH.read_text(encoding="utf-8")

    yield content

    # Teardown: 清理所有中间文件
    for f in _INTERMEDIATE_FILES:
        if f.exists():
            f.unlink()


class TestOldVersionFlag:
    """验证旧版 LGD flag 在完整流程中的类型识别。"""

    def test_lgc_contains_int_type(self, lgc_content):
        """LGC 中应存在 int 类型声明（来自 0xC2 flag）。"""
        assert "int " in lgc_content, (
            "LGC 中未找到 int 类型声明，旧版 0xC2 flag 可能未被正确识别"
        )

    def test_lgc_contains_string_type(self, lgc_content):
        """LGC 中应存在 string 类型声明（来自 0xC1 flag）。"""
        assert "string " in lgc_content, (
            "LGC 中未找到 string 类型声明，旧版 0xC1 flag 可能未被正确识别"
        )

    def test_lgc_no_unknown_int(self, lgc_content):
        """LGC 中不应出现 unknown_int，说明所有 flag 都被正确映射。"""
        assert "unknown_int" not in lgc_content, (
            "LGC 中出现了 unknown_int，说明存在未识别的旧版 flag"
        )
