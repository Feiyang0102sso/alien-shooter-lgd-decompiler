"""
test/test_asm/test_asm_generation.py
对所有 data 目录下的 .lgd 文件的 ASM 生成进行端到端自动化验证。
根据 .lgd 文件名，自动寻找对应的 _expected.csv 进行断言。
"""

import csv
import pytest
from pathlib import Path

# 获取 data 目录的绝对路径
DATA_DIR = Path(__file__).parent / "data"


def _load_expected_csv(lgd_name: str) -> dict:
    """
    根据传入的 lgd 文件名，动态寻找并读取对应的期望 CSV 文件。
    例如: tutorial_00.lgd -> tutorial_00_expected.csv
    """
    # 提取纯文件名 (去掉 .lgd 后缀)
    base_name = Path(lgd_name).stem
    csv_path = DATA_DIR / f"{base_name}_expected.csv"

    expected = {}
    # 如果找不到 CSV，返回空字典
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
# 测试用例 (接收 conftest.py 里配置好的 lgd_session)
# ===========================================================================

def test_total_function_count(lgd_session):
    """动态校验：生成的函数总数必须与对应的 CSV 行数一致。"""
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
    """动态校验：空函数数量必须与 CSV 中标记为 empty 的数量一致。"""
    _, _, asm_functions, lgd_name = lgd_session
    expected_data = _load_expected_csv(lgd_name)

    if not expected_data:
        pytest.skip(f"未找到 {lgd_name} 的期望 CSV，跳过空函数测试。")

    # 从 CSV 数据中统计空函数的期望数量
    expected_empty = sum(1 for v in expected_data.values() if v is None)
    actual = sum(1 for f in asm_functions if f["is_empty"])

    assert actual == expected_empty, (
        f"[{lgd_name}] 空函数数量不符: 期望 {expected_empty}，实际 {actual}\n"
        f"  检测到的空函数: {[f['name'] for f in asm_functions if f['is_empty']]}"
    )


def test_each_function_last_line_num(lgd_session):
    """逐函数比对最后一个 LINE_NUM 与 CSV 期望值。"""
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