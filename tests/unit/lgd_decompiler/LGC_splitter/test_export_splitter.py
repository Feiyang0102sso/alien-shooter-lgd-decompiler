"""
test_export_splitter.py

LGC export 提取与拆分工具的单元测试。
包含自动化 pytest 测试以及支持直接运行的手动入口。
验证是否成功读取 `regression_tutorial_00.lgc` 里的 173 个 extern 声明并能成功写入文件。
"""

import sys
from pathlib import Path
import pytest

from lgd_tool.lgd_decompiler.LGC_splitter.export_splitter import (
    extract_extern_declarations,
    write_export_file,
)


def get_fixture_lgc_path() -> Path:
    """获取 regression_tutorial_00.lgc 的物理路径。"""
    current_file = Path(__file__).resolve()
    # 向上寻找项目根目录 (向上第 5 级)
    # d:\python coding\lgd_tool\tests\unit\lgd_decompiler\LGC_splitter\test_export_splitter.py
    # -> LGC_splitter -> lgd_decompiler -> unit -> tests -> project_root
    project_root = current_file.parents[4]
    lgc_path = project_root / "tests" / "fixtures" / "regression_lgc" / "regression_tutorial_00.lgc"
    return lgc_path


def test_extern_extraction() -> None:
    """
    测试从 regression_tutorial_00.lgc 中成功提取 173 个 extern 声明。
    """
    lgc_path = get_fixture_lgc_path()
    assert lgc_path.exists(), f"测试输入文件不存在: {lgc_path}"

    lgc_content = lgc_path.read_text(encoding="utf-8", errors="replace")
    externs = extract_extern_declarations(lgc_content)

    # 1. 验证数量是否恰好为 173 个
    assert len(externs) == 173, f"预期的 extern 数量为 173，但实际提取到了 {len(externs)} 个"

    # 2. 验证第一个 extern 声明的内容
    # 第一行: extern stackObject(int stackObject_arg0) 100;
    first_expected = "extern stackObject(int stackObject_arg0) 100;"
    assert externs[0] == first_expected, f"第一个 extern 匹配失败，实际为: {externs[0]}"

    # 3. 验证最后一个 extern 声明的内容
    # 最后一行: extern finishResourcesLoad() 255;
    last_expected = "extern finishResourcesLoad() 255;"
    assert externs[-1] == last_expected, f"最后一个 extern 匹配失败，实际为: {externs[-1]}"


def test_export_file_writing(tmp_path: Path) -> None:
    """
    测试将提取的 extern 声明成功写入指定的 core/export.lgc 文件中。
    """
    lgc_path = get_fixture_lgc_path()
    lgc_content = lgc_path.read_text(encoding="utf-8", errors="replace")
    externs = extract_extern_declarations(lgc_content)

    # 定义临时的 core/export.lgc 写入路径
    output_file = tmp_path / "core" / "export.lgc"
    write_export_file(externs, output_file)

    # 验证文件是否已存在
    assert output_file.exists()

    # 验证文件内容
    written_content = output_file.read_text(encoding="utf-8")
    written_lines = written_content.splitlines()

    # 头四行应当是注释信息
    assert written_lines[0] == "// =========================================="
    assert written_lines[1] == "// Export Definitions"
    assert written_lines[2] == "// Total Declarations: 173"
    assert written_lines[3] == "// =========================================="

    # 第 6 行应当是第一个 extern（因为第 5 行为空行）
    assert written_lines[5] == "extern stackObject(int stackObject_arg0) 100;"
