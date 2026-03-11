"""
test/test_asm/test_tutorial00.py
对 tutorial_00.lgd 的 ASM 生成进行端到端验证。

测试点：
1. 函数总数是否为 484
2. 空函数数量是否为 4
3. 逐函数比对最后一个 LINE_NUM 与 CSV 期望值

运行方式（-s 用于允许 input() 交互）：
    python -m pytest test/test_asm/test_tutorial00.py -v -s
"""

import csv
import os


# CSV 期望数据路径
CSV_PATH = os.path.join(os.path.dirname(__file__), "expected_line_nums.csv")

# 硬编码的期望数字（regression 锚点）
EXPECTED_TOTAL_FUNCS = 484
EXPECTED_EMPTY_FUNCS = 5


def _load_expected_csv() -> dict:
    """
    读取 CSV，返回 {函数名: last_line_num} 字典。
    空函数对应值为 None，非空函数为整数。
    """
    expected = {}
    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["FuncName"]
            raw = row["LastLineNum"]
            expected[name] = None if raw == "empty" else int(raw)
    return expected


# ===========================================================================
# 测试用例
# ===========================================================================

def test_total_function_count(tutorial00_session):
    """函数总数必须为 484。"""
    _, _, asm_functions = tutorial00_session
    actual = len(asm_functions)
    assert actual == EXPECTED_TOTAL_FUNCS, (
        f"函数总数不符: 期望 {EXPECTED_TOTAL_FUNCS}，实际 {actual}"
    )


def test_empty_function_count(tutorial00_session):
    """空函数（函数体内无 LINE_NUM）数量必须为 4。"""
    _, _, asm_functions = tutorial00_session
    actual = sum(1 for f in asm_functions if f["is_empty"])
    assert actual == EXPECTED_EMPTY_FUNCS, (
        f"空函数数量不符: 期望 {EXPECTED_EMPTY_FUNCS}，实际 {actual}\n"
        f"  检测到的空函数: {[f['name'] for f in asm_functions if f['is_empty']]}"
    )


def test_each_function_last_line_num(tutorial00_session):
    """
    逐函数比对最后一个 LINE_NUM 与 CSV 期望值。
    - 空函数期望 None
    - 非空函数期望对应整数
    收集所有不匹配项后一次性断言，失败时输出完整列表。
    """
    _, _, asm_functions = tutorial00_session
    expected = _load_expected_csv()

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
            f"以下函数的 last_line_num 与 CSV 不匹配（共 {len(mismatches)} 个）:\n"
            + "\n".join(mismatches)
        )

    assert not error_parts, "\n\n".join(error_parts)
