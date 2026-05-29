"""
test_global_var_splitter.py

LGC 全局变量提取与拆分工具的单元测试。
100% 独立的 pytest 自动化单元测试脚本。
"""

import pytest
from pathlib import Path

from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import (
    extract_globals_from_content,
    write_global_variable_file,
    normalize_decl_text,
)

from tests.utils.global_scanner import scan_globals_statistics


def get_fixture_lgc_path() -> Path:
    """获取 regression_tutorial_00.lgc 的物理路径。"""
    current_file = Path(__file__).resolve()
    project_root = current_file.parents[4]
    lgc_path = project_root / "tests" / "fixtures" / "regression_lgc" / "regression_tutorial_00.lgc"
    return lgc_path


def test_normalize_decl_text() -> None:
    """
    测试变量声明行的宽容归一化处理。
    """
    assert normalize_decl_text("int SoundVolume;") == "int SoundVolume;"
    assert normalize_decl_text("  int   AmmoPrice[11]   ;") == "int AmmoPrice[11] ;"


def test_inline_globals_extraction() -> None:
    """
    测试使用手写构造（Inline）文本，提取全局变量声明。
    """
    sample_content = r"""
    // ==========================================
    // --- Global Variables ---
    int SoundVolume;
    string musicAmbient = "music\\mus00.ogg";
    int AmmoPrice[11] = { 0, 0, 20, 50, 100 };
    // ==========================================
    
    funcA()
    {
        int x = 1;
    }
    """
    globals_list = extract_globals_from_content(sample_content)
    
    assert len(globals_list) == 3
    
    # 验证直接存储的全局变量声明字符串
    assert globals_list[0] == "int SoundVolume;"
    assert globals_list[1] == r'string musicAmbient = "music\\mus00.ogg";'
    assert globals_list[2] == "int AmmoPrice[11] = { 0, 0, 20, 50, 100 };"


def test_real_globals_extraction() -> None:
    """
    测试从真实回归用例 regression_tutorial_00.lgc 提取全局变量。
    """
    lgc_path = get_fixture_lgc_path()
    assert lgc_path.exists()
    
    content = lgc_path.read_text(encoding="utf-8", errors="replace")
    globals_list = extract_globals_from_content(content)
    
    # 确保变量列表不为空且满足数量
    assert len(globals_list) == 165
    
    # 验证首尾全局变量声明内容
    assert globals_list[0] == "int SoundVolume;"
    assert globals_list[-1] == "int StartTeleport = 0;"


def test_regression_globals_classification_statistics() -> None:
    """
    使用从 scripts/lgc_globals_scan/decompiled_global_scan.py 获取的
    回归现场真实统计数据，对真实的 regression_tutorial_00.lgc 全局变量分类数量进行自动化测试。
    """
    lgc_path = get_fixture_lgc_path()
    assert lgc_path.exists()
    
    content = lgc_path.read_text(encoding="utf-8", errors="replace")
    stats = scan_globals_statistics(content)
    
    # 强力回归断言，保障重构后的数据准确性
    assert stats["int"] == 115, f"预期 int 数量为 115，实际为 {stats['int']}"
    assert stats["string"] == 10, f"预期 string 数量为 10，实际为 {stats['string']}"
    assert stats["int[]"] == 39, f"预期 int[] 数量为 39，实际为 {stats['int[]']}"
    assert stats["string[]"] == 1, f"预期 string[] 数量为 1，实际为 {stats['string[]']}"
    assert stats["total"] == 165, f"预期全局变量总数为 165，实际为 {stats['total']}"


def test_globals_writing(tmp_path: Path) -> None:
    """
    测试成功写出 core/global_variable.lgc 并比对内容。
    """
    lgc_path = get_fixture_lgc_path()
    content = lgc_path.read_text(encoding="utf-8", errors="replace")
    globals_list = extract_globals_from_content(content)
    
    output_file = tmp_path / "core" / "global_variable.lgc"
    write_global_variable_file(globals_list, output_file)
    
    assert output_file.exists()
    
    written = output_file.read_text(encoding="utf-8")
    lines = written.splitlines()
    
    # 头三行应当是 Sentinel 防重包含保护
    assert lines[0] == "#ifndef _CORE_GLOBAL_VARIABLE_LGC_"
    assert lines[1] == "#define _CORE_GLOBAL_VARIABLE_LGC_ aaa"
    assert lines[2] == ""

    # 注释信息
    assert lines[3] == "// =========================================="
    assert lines[4] == "// Public Global Variables"
    assert lines[6] == "// =========================================="
    
    # 第 9 行应当是第一个全局变量（因为第 8 行为空行）
    assert lines[8] == "int SoundVolume;"

    # 尾部应当以 #endif 结束
    assert written.strip().endswith("#endif")

    # 测试完成后，显式干掉产生的文件与空目录，保持绝对清洁 (Wipe)
    if output_file.exists():
        output_file.unlink()
        
    core_dir = output_file.parent
    if core_dir.exists():
        # 如果 core_dir 已经为空，则顺手删除它以保持完美零残留
        if len(list(core_dir.iterdir())) == 0:
            core_dir.rmdir()
