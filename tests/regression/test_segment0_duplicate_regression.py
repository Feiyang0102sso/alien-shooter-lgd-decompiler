"""
tests/regression/test_segment0_duplicate_regression.py
回归测试：空函数 defines() 在不同地图中前驱不同，曾导致 segment 0 分裂成两个版本，
core/export.lgc 同时 include 两者，编译报 Function redefinition。

fixture 链路（用例名 segment0_duplicate）：
  original_lgc/segment0_duplicate/   源码，编译得到 ↓
  lgd_files/segment0_duplicate/      test.lgd / main.lgd，反编译得到 ↓
  reorganize_lgc/segment0_duplicate/ 未拆分的大 LGC，本回归的直接输入（与反编译器解耦）

  test.lgc : common(add sub) | defines(defines) | state(twice half) | main()
  main.lgc : common(add sub) | extra(mul div) | defines(defines) | state(twice half) | main()
"""

import re
import shutil
from pathlib import Path

import pytest

from lgd_tool.lgd_decompiler.LGC_reorganizer import parse_lgc_functions, run_splitter_pipeline
from tests.conftest import REORGANIZE_LGC_DIR, TESTS_DIR

# ===== 常量配置 =====
FIXTURE_DIR = REORGANIZE_LGC_DIR / "segment0_duplicate"
MAP_NAMES = ["main", "test"]
WORK_DIR = TESTS_DIR / "output" / "segment0_duplicate"
INCLUDE_PATTERN = re.compile(r'^\s*#include\s+"([^"]+)"', re.MULTILINE)
SEGMENT_INCLUDE_PREFIX = '#include "segment_'


@pytest.fixture(scope="module")
def reorganized_dir():
    """
    把未拆分的大 LGC 复制到独立工作目录并执行多文件重组，返回工作目录。
    测试全部通过后清理工作目录。
    """
    if WORK_DIR.exists():
        shutil.rmtree(WORK_DIR)
    WORK_DIR.mkdir(parents=True)

    # 重组只按 .lgd 路径定位同名 .lgc，不读取 .lgd 本身，因此无需真实 lgd 文件
    success_list = []
    for name in MAP_NAMES:
        shutil.copy2(FIXTURE_DIR / f"{name}.lgc", WORK_DIR / f"{name}.lgc")
        success_list.append(str(WORK_DIR / f"{name}.lgd"))

    run_splitter_pipeline(WORK_DIR, success_list=success_list)

    yield WORK_DIR

    shutil.rmtree(WORK_DIR)


def _collect_defined_functions(root_dir: Path, entry_file: Path) -> list[str]:
    """
    从入口文件出发递归展开 #include（每个文件只展开一次，等价于 include guard），
    收集最终参与编译的全部函数名，重复定义会在列表中出现多次。

    :param root_dir: include 相对路径的根目录
    :param entry_file: 入口地图脚本
    :return: 按出现顺序排列的函数名列表
    """
    visited = set()
    func_names = []
    pending_files = [entry_file]

    while len(pending_files) > 0:
        current = pending_files.pop(0)
        if current in visited:
            continue
        visited.add(current)

        content = current.read_text(encoding="utf-8")
        for include_path in INCLUDE_PATTERN.findall(content):
            pending_files.append(root_dir / include_path.replace("\\", "/"))

        for func in parse_lgc_functions(content):
            func_names.append(func.name)

    return func_names


class TestSegment0DuplicateRegression:
    """
    测试类：验证 export.lgc 只引用唯一的 segment 0，且各地图不存在重复定义的函数。
    """

    def test_export_includes_single_segment0(self, reorganized_dir: Path):
        """
        export.lgc 被所有地图共享，只能 include 一个 segment 0。
        """
        export_text = (reorganized_dir / "core" / "export.lgc").read_text(encoding="utf-8")
        segment_include_count = export_text.count(SEGMENT_INCLUDE_PREFIX)
        assert segment_include_count == 1, f"export.lgc includes {segment_include_count} segments:\n{export_text}"

    def test_boundary_empty_func_split_into_empty_segment(self, reorganized_dir: Path):
        """
        边界空函数 defines() 应单独写入唯一的 segment_XX.empty.lgc，并被两张地图共享。
        """
        empty_segments = sorted(reorganized_dir.glob("segment_*.empty.lgc"))
        assert len(empty_segments) == 1, f"Expected exactly one empty segment, got: {empty_segments}"

        empty_funcs = parse_lgc_functions(empty_segments[0].read_text(encoding="utf-8"))
        assert len(empty_funcs) == 1
        assert empty_funcs[0].name == "defines"

    @pytest.mark.parametrize("map_name", MAP_NAMES)
    def test_no_duplicate_function_definition(self, reorganized_dir: Path, map_name: str):
        """
        展开全部 include 后，每个函数在地图中只能被定义一次（对应编译器的 Function redefinition）。
        """
        func_names = _collect_defined_functions(reorganized_dir, reorganized_dir / f"{map_name}.lgc")

        duplicates = []
        seen = set()
        for name in func_names:
            if name in seen:
                duplicates.append(name)
            seen.add(name)

        assert len(duplicates) == 0, f"{map_name}.lgc has duplicate functions: {duplicates}"
        assert "defines" in seen, f"{map_name}.lgc lost defines() after reorganize"
