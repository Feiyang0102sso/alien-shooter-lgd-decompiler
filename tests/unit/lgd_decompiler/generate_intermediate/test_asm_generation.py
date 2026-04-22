"""
tests/unit/lgd_decompiler/generate_intermediate/test_asm_generation.py

for each lgd, auto find corresponding _expected.csv for asserts
"""

import csv
import pytest

from tests.conftest import EXPECTED_CSV_DIR


def _load_expected_csv(lgd_name: str) -> dict:
    """
    find expected csv file

    eg: tutorial_00.lgd -> tutorial_00_expected.csv
    """
    from pathlib import Path
    base_name = Path(lgd_name).stem
    csv_path = EXPECTED_CSV_DIR / f"{base_name}_expected.csv"

    expected = {}
    if not csv_path.exists():
        return {}

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["FuncName"]
            raw = row["LastLineNum"]
            expected[name] = None if raw == "empty" else int(raw)

    return expected


# ===========================================================================
# test cases
# ===========================================================================

def test_total_function_count(lgd_session):
    """asserts: func num == defined in csv?"""
    _, _, asm_functions, lgd_name = lgd_session
    expected_data = _load_expected_csv(lgd_name)

    if not expected_data:
        pytest.skip(f"未找到 {lgd_name} 的期望 CSV，跳过总数测试。")

    expected_total = len(expected_data)
    actual = len(asm_functions)

    assert actual == expected_total, (
        f"[{lgd_name}] 函数总数不符: 期望 {expected_total}，实际 {actual}"
    )


def test_empty_function_count(lgd_session):
    """asserts: empty func num == empty in csv?"""
    _, _, asm_functions, lgd_name = lgd_session
    expected_data = _load_expected_csv(lgd_name)

    if not expected_data:
        pytest.skip(f"未找到 {lgd_name} 的期望 CSV，跳过空函数测试。")

    # Estimate the Expected Number of Empty Functions from CSV Data
    expected_empty = sum(1 for v in expected_data.values() if v is None)
    actual = sum(1 for f in asm_functions if f["is_empty"])

    assert actual == expected_empty, (
        f"[{lgd_name}] 空函数数量不符: 期望 {expected_empty}，实际 {actual}\n"
        f"  检测到的空函数: {[f['name'] for f in asm_functions if f['is_empty']]}"
    )


def test_each_function_last_line_num(lgd_session):
    """asserts: func last line == defined in csv?"""
    _, _, asm_functions, lgd_name = lgd_session
    expected = _load_expected_csv(lgd_name)

    if not expected:
        pytest.skip(f"未找到 {lgd_name} 的期望 CSV，跳过行号比对测试。")

    mismatches = []
    missing_in_csv = []

    for func in asm_functions:
        name = func["name"]
        actual = func["last_line_num"]

        if name not in expected:
            missing_in_csv.append(name)
            continue

        exp = expected[name]
        if actual != exp:
            mismatches.append(
                f"  [{name}] 期望={exp!r}  实际={actual!r}"
            )

    error_parts = []
    if missing_in_csv:
        error_parts.append(
            f"以下函数在 CSV 中未找到（共 {len(missing_in_csv)} 个）:\n"
            + "\n".join(f"  - {n}" for n in missing_in_csv)
        )
    if mismatches:
        error_parts.append(
            f"[{lgd_name}] 以下函数的 last_line_num 与 CSV 不匹配（共 {len(mismatches)} 个）:\n"
            + "\n".join(mismatches)
        )

    assert not error_parts, "\n\n".join(error_parts)
