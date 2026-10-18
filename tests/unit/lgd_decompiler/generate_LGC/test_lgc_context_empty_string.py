"""
tests/unit/lgd_decompiler/generate_LGC/test_lgc_context_empty_string.py
测试 LgcContext 对字符串空串的还原：
- 三条数组路径（全局数组 / 数组参数默认值 / static 局部数组）中 JSON "" 还原为 ""
- 数组中真实存储为两个双引号字符的字符串原样还原为 "\"\""，与空串区分
- 标量空串占位符仍按原样还原
"""

import csv
import json
from pathlib import Path

import pytest

from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.generate_LGC.lgc_context import LgcContext

CSV_HEADERS = [
    "Global_ID", "P1_Index", "File_ID", "Name", "Category", "Type",
    "Is_Array", "Size", "Is_Initialized", "Init_Value", "Extern_ID", "Param_Types",
]
# exporter_csv 中标量空串的占位符（两个双引号字符）
PLACEHOLDER = '""'


@pytest.fixture
def stop_on_error():
    """开启 stop_on_error，使 error_and_stop 抛出 FatalError，测试后恢复。"""
    logger.set_stop_on_error(True)
    yield
    logger.set_stop_on_error(False)


def _row(global_id: int, name: str, category: str, type_name: str,
         is_array: bool, size: int, init_value: str, param_types: str = "\tN/A") -> dict:
    """按 exporter_csv 的格式（数值列带前导 \\t）构造一行。"""
    return {
        "Global_ID": f"\t{global_id}",
        "P1_Index": "\t0",
        "File_ID": "\t0",
        "Name": name,
        "Category": category,
        "Type": type_name,
        "Is_Array": f"\t{is_array}",
        "Size": f"\t{size}",
        "Is_Initialized": "\tTrue",
        "Init_Value": init_value,
        "Extern_ID": "\tN/A",
        "Param_Types": param_types,
    }


def _load_context(tmp_path: Path, rows: list) -> LgcContext:
    """写出 CSV 并加载为 LgcContext。"""
    csv_path = tmp_path / "test.lgd.csv"
    with open(csv_path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    context = LgcContext()
    context.load_from_csv(str(csv_path))
    return context


def test_empty_string_in_all_array_paths(tmp_path: Path, stop_on_error) -> None:
    """
    JSON "" 在全局数组、数组参数默认值、static 局部数组中均还原为 ""。
    """
    rows = [
        _row(0, "items", "VAR", "string", True, 4, json.dumps(["a", "b", "c", ""])),
        _row(1, "pick", "FUNC", "\tN/A", False, 1, "\tN/A", "string"),
        _row(1, "pick_arg0", "PARAM", "string", True, 2, json.dumps(["x", ""])),
        _row(2, "main", "FUNC", "\tN/A", False, 0, "\tN/A"),
        _row(2, "main@local0", "LOCAL_VAR", "string", True, 3, json.dumps(["t1", "", "t3"])),
    ]
    context = _load_context(tmp_path, rows)

    assert 'string items[4] = { "a", "b", "c", "" };' in context.header_manager.globals
    assert 'string pick_arg0[2] = { "x", "" }' in context.func_params["pick"]
    assert 'static string main_local0[3] = { "t1", "", "t3" };' in context.func_locals["main"]


def test_literal_two_quote_string_in_array_kept(tmp_path: Path, stop_on_error) -> None:
    """
    数组元素的值与二进制一致：真实存储为两个双引号字符的字符串（如 ASF453 Supply_table）
    必须原样还原为 "\\"\\""，并与空串 "" 区分开。
    """
    rows = [
        _row(0, "quoted", "VAR", "string", True, 2, json.dumps([PLACEHOLDER, ""])),
    ]
    context = _load_context(tmp_path, rows)

    assert 'string quoted[2] = { "\\"\\"", "" };' in context.header_manager.globals


def test_scalar_empty_string_placeholder_kept(tmp_path: Path, stop_on_error) -> None:
    """
    标量仍使用占位符表示空串，还原为 ""，行为不变。
    """
    rows = [
        _row(0, "title", "VAR", "string", False, 1, PLACEHOLDER),
    ]
    context = _load_context(tmp_path, rows)

    assert 'string title = "";' in context.header_manager.globals
