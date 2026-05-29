"""
test_global_var_merger.py

针对 LGC 拆分器中全局变量（Global Variables）合并、差异化局部注入与警报功能的单元测试。
"""

import pytest
from pathlib import Path
from lgd_tool.lgd_decompiler.LGC_splitter import (
    extract_variable_name,
    process_global_variables,
)


def test_extract_variable_name() -> None:
    """
    测试从各种全局变量声明字符串中提取纯变量名称。
    """
    assert extract_variable_name("int SoundVolume;") == "SoundVolume"
    assert extract_variable_name("  string   musicAmbient   =   \"music\\\\mus00.ogg\"  ;") == "musicAmbient"
    assert extract_variable_name("int AmmoPrice[11] = { 0, 0, 20 };") == "AmmoPrice"
    assert extract_variable_name("int StartTeleport = 0;") == "StartTeleport"


def test_process_globals_all_identical(tmp_path: Path) -> None:
    """
    测试 1：当多个文件的全局变量完全相同且没有冲突时：
    1. 所有的变量被成功作为公共变量写入公共 core/global_variable.lgc。
    2. 主脚本入口段（最后一个段）没有任何本地注入。
    """
    file_to_globals = {
        "tutorial_00.lgc": [
            "int SoundVolume;",
            "int StartTeleport = 0;",
        ],
        "tutorial_01.lgc": [
            "  int SoundVolume;  ",
            "int StartTeleport = 0;",
        ]
    }

    # 调用全局变量合流核心方法
    file_local_injections = process_global_variables(
        file_to_globals=file_to_globals,
        output_dir=tmp_path
    )

    # 1. 验证公共文件是否被顺利写出
    public_file = tmp_path / "core" / "global_variable.lgc"
    assert public_file.exists()
    
    written_text = public_file.read_text(encoding="utf-8")
    assert "int SoundVolume;" in written_text
    assert "int StartTeleport = 0;" in written_text

    # 2. 验证主入口没有发生任何本地局部变量注入（注入列表为空）
    assert len(file_local_injections["tutorial_00.lgc"]) == 0
    assert len(file_local_injections["tutorial_01.lgc"]) == 0


def test_process_globals_with_conflicts_and_uniques(tmp_path: Path) -> None:
    """
    测试 2：当全局变量存在定义冲突，或者只被部分文件独占时：
    1. 一致的变量（以及仅被个别文件独占但没有冲突的变量）合入公共文件。
    2. 不一致（有定义冲突）的变量不合入公共文件。
    3. 有定义冲突的变量被精准地注入到各自文件的最后一个段脚本（主入口）头部。
    """
    file_to_globals = {
        "tutorial_00.lgc": [
            "int SoundVolume;",          # 公共变量（完全一致）
            "int StartTeleport = 0;",    # 冲突变量：本文件初始值为 0
            "int MapOnlyVar = 99;",      # 独占且无冲突变量：应算公共！
        ],
        "tutorial_01.lgc": [
            "int SoundVolume;",          # 公共变量（完全一致）
            "int StartTeleport = 1;",    # 冲突变量：本文件初始值为 1
        ]
    }

    file_local_injections = process_global_variables(
        file_to_globals=file_to_globals,
        output_dir=tmp_path
    )

    # 1. 验证公共全局变量文件：包含公共的 SoundVolume 和独占无冲突的 MapOnlyVar，不含冲突的 StartTeleport
    public_file = tmp_path / "core" / "global_variable.lgc"
    assert public_file.exists()
    written_text = public_file.read_text(encoding="utf-8")
    assert "int SoundVolume;" in written_text
    assert "int MapOnlyVar = 99;" in written_text
    assert "StartTeleport" not in written_text

    # 2. 验证私有变量定义的分发
    # tutorial_00.lgc 应分发了具有冲突的 StartTeleport = 0
    decls_00 = file_local_injections["tutorial_00.lgc"]
    assert len(decls_00) == 1
    assert decls_00[0] == "int StartTeleport = 0;"

    # tutorial_01.lgc 应分发了具有冲突的 StartTeleport = 1
    decls_01 = file_local_injections["tutorial_01.lgc"]
    assert len(decls_01) == 1
    assert decls_01[0] == "int StartTeleport = 1;"

