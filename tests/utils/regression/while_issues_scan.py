"""
tests/utils/regression/while_issues_scan.py

扫描 LGC 中可疑的 while（逻辑抄自 scripts/endless_loop_detect/scan_while_issues.py）：
  1. while (1) { ... }              — WARNING（可能是 do-while 结构化结果）
  2. while (func(...)) { }          — WARNING（空循环体，条件为函数调用）
  3. while (其它条件) { }         — ERROR（空循环体，多为反编译问题）
"""

import re
from dataclasses import dataclass
from pathlib import Path


# 空 while 花括号内允许的最大行数（含仅空白/注释的行）
MAX_EMPTY_WHILE_BODY_LINES = 12

RESERVED_TOP_LEVEL_NAMES = frozenset(
    ("if", "while", "for", "switch", "else", "iff", "extern")
)

WHILE_ONE_PATTERN = re.compile(r"while\s*\(\s*1\s*\)")
WHILE_HEAD_PATTERN = re.compile(r"^(\s*)while\s*\((.+)\)\s*(\{?)\s*$")
FUNC_NAME_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*\(")

ISSUE_WARNING = "WARNING"
ISSUE_ERROR = "ERROR"


@dataclass
class WhileIssue:
    """单条 while 问题记录。"""

    lgc_path: Path
    function_name: str
    func_start_line: int
    issue_type: str
    severity: str
    while_line_in_func: int
    file_line_number: int
    line_content: str
    body_line_count: int
    body_preview: str


@dataclass
class FunctionSpan:
    """顶层方法在文件中的范围。"""

    name: str
    start_line: int
    lines: list[str]


def split_top_level_functions(lgc_path: Path) -> list[FunctionSpan]:
    """
    将 LGC 切分为顶层方法列表（含文件行号）。
    """
    all_lines = lgc_path.read_text(encoding="utf-8", errors="replace").splitlines()
    functions: list[FunctionSpan] = []
    current_name = ""
    current_lines: list[str] = []
    func_start_line = 0
    depth = 0
    in_function = False

    for file_line_no, line in enumerate(all_lines, start=1):
        stripped = line.strip()
        if not in_function:
            sig_match = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\([^)]*\)\s*$", line)
            if sig_match is None:
                continue
            name = sig_match.group(1)
            if name in RESERVED_TOP_LEVEL_NAMES:
                continue
            current_name = name
            current_lines = [line]
            func_start_line = file_line_no
            in_function = True
            depth = 0
            continue

        current_lines.append(line)
        depth += line.count("{")
        depth -= line.count("}")
        if depth <= 0 and stripped == "}":
            functions.append(
                FunctionSpan(
                    name=current_name,
                    start_line=func_start_line,
                    lines=current_lines,
                )
            )
            in_function = False
            current_name = ""
            current_lines = []

    return functions


def is_trivial_line(line: str) -> bool:
    """空白或注释行，不算有效语句。"""
    text = line.strip()
    if text == "":
        return True
    if text.startswith("//"):
        return True
    return False


def is_single_function_call_condition(condition: str) -> bool:
    """
    while 条件是否为单一函数调用，例如 changeLoadingElementTag(a, b, "tag_")。
    """
    text = condition.strip()
    if text == "":
        return False
    if FUNC_NAME_PATTERN.match(text) is None:
        return False

    open_paren_idx = text.find("(")
    depth = 0
    close_paren_idx = -1
    for idx in range(open_paren_idx, len(text)):
        ch = text[idx]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                close_paren_idx = idx
                break

    if close_paren_idx < 0:
        return False

    rest = text[close_paren_idx + 1 :].strip()
    if rest != "":
        return False

    return True


def is_empty_statement_block(inner_lines: list[str]) -> bool:
    """花括号内是否无有效语句。"""
    for line in inner_lines:
        if not is_trivial_line(line):
            return False
    return True


def extract_while_blocks(func_lines: list[str]) -> list[dict]:
    """
    在方法体内找出所有 while 语句块。
    支持 while (...) { 同一行，或 while (...) 与 { 分两行。
    """
    blocks: list[dict] = []
    line_idx = 0
    total = len(func_lines)

    while line_idx < total:
        line = func_lines[line_idx]
        head_match = WHILE_HEAD_PATTERN.match(line)
        if head_match is None:
            line_idx += 1
            continue

        brace_on_same_line = head_match.group(3) == "{"
        body_start_idx = line_idx + 1
        brace_depth = 0

        if brace_on_same_line:
            brace_depth = 1
        else:
            if body_start_idx >= total:
                line_idx += 1
                continue
            next_line = func_lines[body_start_idx].strip()
            if next_line != "{":
                line_idx += 1
                continue
            brace_depth = 1
            body_start_idx = line_idx + 2

        body_lines: list[str] = []
        scan_idx = body_start_idx
        while scan_idx < total and brace_depth > 0:
            body_line = func_lines[scan_idx]
            body_lines.append(body_line)
            brace_depth += body_line.count("{")
            brace_depth -= body_line.count("}")
            scan_idx += 1

        inner_lines: list[str] = []
        if len(body_lines) >= 1:
            inner_lines = body_lines[:-1]

        blocks.append(
            {
                "while_line_idx": line_idx,
                "while_line": line,
                "inner_lines": inner_lines,
                "body_line_count": len(inner_lines),
                "next_idx": scan_idx,
            }
        )
        line_idx = scan_idx

    return blocks


def format_body_preview(inner_lines: list[str]) -> str:
    """空循环体预览（最多 3 行）。"""
    if not inner_lines:
        return "(empty)"
    parts: list[str] = []
    limit = 3
    count = 0
    for line in inner_lines:
        parts.append(line.rstrip())
        count += 1
        if count >= limit:
            break
    if len(inner_lines) > limit:
        parts.append("...")
    return " | ".join(parts)


def scan_function_for_while_issues(
    lgc_path: Path,
    func_span: FunctionSpan,
) -> list[WhileIssue]:
    """扫描单个方法内的 while(1) 与空 while。"""
    issues: list[WhileIssue] = []
    blocks = extract_while_blocks(func_span.lines)

    for block in blocks:
        line_idx = block["while_line_idx"]
        line = block["while_line"]
        inner_lines = block["inner_lines"]
        body_line_count = block["body_line_count"]
        file_line_no = func_span.start_line + line_idx

        if WHILE_ONE_PATTERN.search(line):
            issues.append(
                WhileIssue(
                    lgc_path=lgc_path,
                    function_name=func_span.name,
                    func_start_line=func_span.start_line,
                    issue_type="while(1)",
                    severity=ISSUE_WARNING,
                    while_line_in_func=line_idx + 1,
                    file_line_number=file_line_no,
                    line_content=line.rstrip(),
                    body_line_count=body_line_count,
                    body_preview=format_body_preview(inner_lines),
                )
            )
            continue

        if body_line_count > MAX_EMPTY_WHILE_BODY_LINES:
            continue
        if not is_empty_statement_block(inner_lines):
            continue

        head_match = WHILE_HEAD_PATTERN.match(line)
        condition_text = ""
        if head_match is not None:
            condition_text = head_match.group(2)

        if is_single_function_call_condition(condition_text):
            issue_type = "empty_while_func"
            severity = ISSUE_WARNING
        else:
            issue_type = "empty_while"
            severity = ISSUE_ERROR

        issues.append(
            WhileIssue(
                lgc_path=lgc_path,
                function_name=func_span.name,
                func_start_line=func_span.start_line,
                issue_type=issue_type,
                severity=severity,
                while_line_in_func=line_idx + 1,
                file_line_number=file_line_no,
                line_content=line.rstrip(),
                body_line_count=body_line_count,
                body_preview=format_body_preview(inner_lines),
            )
        )

    return issues


def dedupe_issues(issues: list[WhileIssue]) -> list[WhileIssue]:
    """同一文件、同一方法、同一行只保留一条。"""
    seen: set[tuple[str, str, int, str]] = set()
    result: list[WhileIssue] = []
    for issue in issues:
        key = (
            issue.lgc_path.name,
            issue.function_name,
            issue.file_line_number,
            issue.issue_type,
        )
        if key in seen:
            continue
        seen.add(key)
        result.append(issue)
    return result


def scan_lgc_file(lgc_path: Path) -> list[WhileIssue]:
    """扫描单个 LGC 文件。"""
    all_issues: list[WhileIssue] = []
    functions = split_top_level_functions(lgc_path)
    for func_span in functions:
        found = scan_function_for_while_issues(lgc_path, func_span)
        for item in found:
            all_issues.append(item)
    return dedupe_issues(all_issues)


def count_issues_by_type(issues: list[WhileIssue]) -> dict[str, int]:
    """按 issue_type 统计条数。"""
    counts: dict[str, int] = {}
    for issue in issues:
        if issue.issue_type not in counts:
            counts[issue.issue_type] = 0
        counts[issue.issue_type] += 1
    return counts


def count_error_issues(issues: list[WhileIssue]) -> int:
    """ERROR 级别问题数量。"""
    total = 0
    for issue in issues:
        if issue.severity == ISSUE_ERROR:
            total += 1
    return total


def while_one_block_has_break(inner_lines: list[str]) -> bool:
    """while(1) 循环体内是否包含 break。"""
    for line in inner_lines:
        stripped = line.strip()
        if stripped == "break" or stripped.startswith("break "):
            return True
        if stripped.endswith("break;") or " break;" in stripped:
            return True
    return False


def find_while_one_without_break(lgc_path: Path) -> list[str]:
    """
    返回 while(1) 循环体内缺少 break 的方法名列表。
    """
    missing: list[str] = []
    functions = split_top_level_functions(lgc_path)
    for func_span in functions:
        blocks = extract_while_blocks(func_span.lines)
        for block in blocks:
            line = block["while_line"]
            if WHILE_ONE_PATTERN.search(line) is None:
                continue
            if not while_one_block_has_break(block["inner_lines"]):
                missing.append(func_span.name)
    return missing
