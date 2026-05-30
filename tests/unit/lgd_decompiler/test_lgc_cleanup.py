"""
tests/unit/lgd_decompiler/test_lgc_cleanup.py
测试 main.py 中封装的前置 LGC 冲突清理模块。
"""

import sys
from pathlib import Path
from unittest.mock import patch
import pytest

from lgd_tool.main import cleanup_existing_lgc_files


def test_cleanup_no_lgc_files(tmp_path: Path):
    """
    测试当目录下没有任何 .lgc 文件时，该方法应当直接返回 True。
    """
    # 模拟一个没有任何 .lgc 文件的临时文件夹
    res = cleanup_existing_lgc_files(tmp_path)
    assert res is True


def test_cleanup_cancelled_by_user(tmp_path: Path):
    """
    测试当目录下有 .lgc 文件但用户输入 n 取消时，该方法应当返回 False，且文件不能被删除。
    """
    # 创建一个测试用的 .lgc 文件
    test_file = tmp_path / "test.lgc"
    test_file.write_text("dummy", encoding="utf-8")

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    test_sub_file = sub_dir / "child.lgc"
    test_sub_file.write_text("dummy2", encoding="utf-8")

    # Mock input 返回 n (取消)
    with patch("builtins.input", return_value="n"):
        res = cleanup_existing_lgc_files(tmp_path)

    # 应该返回 False 表示取消
    assert res is False
    # 物理文件依然应当完好无损存在
    assert test_file.exists() is True
    assert test_sub_file.exists() is True


def test_cleanup_confirmed_by_user(tmp_path: Path):
    """
    测试当目录下有 .lgc 文件且用户输入 y 确认时，该方法应当返回 True，且将文件清空。
    """
    # 创建测试文件
    test_file = tmp_path / "test.lgc"
    test_file.write_text("dummy", encoding="utf-8")

    sub_dir = tmp_path / "sub"
    sub_dir.mkdir()
    test_sub_file = sub_dir / "child.lgc"
    test_sub_file.write_text("dummy2", encoding="utf-8")

    # 创建一个非 .lgc 文件作为对照组以保证不会误删其他后缀文件
    safe_file = tmp_path / "safe.txt"
    safe_file.write_text("do not delete", encoding="utf-8")

    # Mock input 返回 y (同意)
    with patch("builtins.input", return_value="y"):
        res = cleanup_existing_lgc_files(tmp_path)

    # 应该返回 True 表示成功清理
    assert res is True
    # .lgc 文件应当被物理删除
    assert test_file.exists() is False
    assert test_sub_file.exists() is False
    # 对照组的非 .lgc 文件应当安然无恙存在
    assert safe_file.exists() is True
