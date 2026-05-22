"""
scripts/endless_loop_detect/scan_while_issues.py

扫描 LGC 中可疑的 while：
  1. while (1) { ... }              — [WARNING] 不一定是 bug（可能是 do-while）
  2. while (func(...)) { }          — [WARNING] 空循环体但条件为函数调用（函数内可能改状态）
  3. while (其它条件) { }         — [ERROR]   空循环体，多为反编译问题

按顶层方法汇总，输出行号与该行原文。
支持单个 .lgc 文件或整个目录（递归 *.lgc）。
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union

from lgd_tool.logger import logger

# ========== 硬编码路径（：单个 .lgc 或目录，str / Path 均可） ==========
TARGET_LGC_PATH: Union[str, Path] = r"D:\python coding\lgd_tool\_project_proceeds\endless_loop\main.lgc"

# 报告输出；None 则只打印到控制台
OUTPUT_REPORT: Union[str, Path, None] = (
    Path(__file__).resolve().parent / "while_issues_report.txt"
)

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


def resolve_path(value: Union[str, Path, None]) -> Optional[Path]:
    """将配置路径转为 Path。"""
    if value is None:
        return None
    return Path(value).expanduser()


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
    """
    空白或注释行，不算有效语句。
    """
    text = line.strip()
    if text == "":
        return True
    if text.startswith("//"):
        return True
    return False


def is_single_function_call_condition(condition: str) -> bool:
    """
    while 条件是否为单一函数调用，例如 changeLoadingElementTag(a, b, "tag_")。
    此类空循环体函数内部可能更新状态，不宜一律判为 ERROR。
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
    """
    花括号内是否无有效语句。
    """
    for line in inner_lines:
        if not is_trivial_line(line):
            return False
    return True


def extract_while_blocks(func_lines: list[str]) -> list[dict]:
    """
    在方法体内找出所有 while 语句块。
    支持 while (...) { 同一行，或 while (...) 与 { 分两行。

    Returns:
        列表元素含 while_line_idx, while_line, inner_lines, body_line_count
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


def scan_function_for_while_issues(
    lgc_path: Path,
    func_span: FunctionSpan,
) -> list[WhileIssue]:
    """
    扫描单个方法内的 while(1) 与空 while。
    """
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


def format_body_preview(inner_lines: list[str]) -> str:
    """
    空循环体预览（最多 3 行）。
    """
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


def dedupe_issues(issues: list[WhileIssue]) -> list[WhileIssue]:
    """
    同一文件、同一方法、同一行只保留一条。
    """
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


def collect_lgc_files(target: Path) -> list[Path]:
    """
    根据路径收集待扫描的 .lgc：单文件或目录递归。
    """
    if not target.exists():
        return []

    if target.is_file():
        if target.suffix.lower() == ".lgc":
            return [target]
        return []

    if target.is_dir():
        result: list[Path] = []
        for path in sorted(target.rglob("*.lgc")):
            if path.is_file():
                result.append(path)
        return result

    return []


def scan_lgc_file(lgc_path: Path) -> list[WhileIssue]:
    """
    扫描单个 LGC 文件。
    """
    all_issues: list[WhileIssue] = []
    functions = split_top_level_functions(lgc_path)
    for func_span in functions:
        found = scan_function_for_while_issues(lgc_path, func_span)
        for item in found:
            all_issues.append(item)
    return all_issues


def scan_lgc_paths(lgc_files: list[Path]) -> list[WhileIssue]:
    """
    扫描多个 LGC 文件并去重。
    """
    all_issues: list[WhileIssue] = []
    for lgc_path in lgc_files:
        found = scan_lgc_file(lgc_path)
        for item in found:
            all_issues.append(item)
    return dedupe_issues(all_issues)


def log_issues(issues: list[WhileIssue]) -> None:
    """
    按 severity 输出到 logger：while(1)、empty_while_func=WARNING，empty_while=ERROR。
    """
    for issue in issues:
        message = (
            "%s:%d %s() %s | func line %d | %s"
            % (
                issue.lgc_path.name,
                issue.file_line_number,
                issue.function_name,
                issue.issue_type,
                issue.while_line_in_func,
                issue.line_content.strip(),
            )
        )
        if issue.severity == ISSUE_ERROR:
            logger.error(message)
        else:
            logger.warning(message)


def format_report(issues: list[WhileIssue], target_label: str) -> str:
    """
    按文件、方法整理文本报告。
    """
    lines: list[str] = []
    lines.append("=" * 72)
    lines.append("While Issues Scan Report")
    lines.append("Target: %s" % target_label)
    lines.append("  while(1)            -> WARNING (may be valid do-while)")
    lines.append("  empty_while_func   -> WARNING (func call may update state)")
    lines.append("  empty_while        -> ERROR (decompiler bug)")
    lines.append("=" * 72)
    lines.append("")

    if not issues:
        lines.append("No while(1) or empty while found.")
        return "\n".join(lines) + "\n"

    by_file: dict[str, list[WhileIssue]] = {}
    for issue in issues:
        key = issue.lgc_path.name
        if key not in by_file:
            by_file[key] = []
        by_file[key].append(issue)

    for file_name in sorted(by_file.keys()):
        file_issues = by_file[file_name]
        lines.append("-" * 72)
        lines.append("FILE: %s" % file_name)
        lines.append("-" * 72)

        by_func: dict[str, list[WhileIssue]] = {}
        for issue in file_issues:
            if issue.function_name not in by_func:
                by_func[issue.function_name] = []
            by_func[issue.function_name].append(issue)

        for func_name in sorted(by_func.keys()):
            func_issues = by_func[func_name]
            func_start = func_issues[0].func_start_line
            lines.append("")
            lines.append("  METHOD: %s()  (starts at line %d)" % (func_name, func_start))

            for issue in func_issues:
                lines.append(
                    "    [%s] [%s] file line %d | func line %d | body lines: %d"
                    % (
                        issue.severity,
                        issue.issue_type,
                        issue.file_line_number,
                        issue.while_line_in_func,
                        issue.body_line_count,
                    )
                )
                lines.append("      %s" % issue.line_content)
                if issue.issue_type in ("empty_while", "empty_while_func"):
                    lines.append("      body: %s" % issue.body_preview)

        lines.append("")

    lines.append("=" * 72)
    lines.append("Summary: %d issue(s) in %d file(s)" % (len(issues), len(by_file)))
    while_one_count = 0
    empty_func_count = 0
    empty_count = 0
    for issue in issues:
        if issue.issue_type == "while(1)":
            while_one_count += 1
        elif issue.issue_type == "empty_while_func":
            empty_func_count += 1
        else:
            empty_count += 1
    lines.append("  WARNING while(1): %d" % while_one_count)
    lines.append("  WARNING empty_while_func: %d" % empty_func_count)
    lines.append("  ERROR   empty_while: %d" % empty_count)
    lines.append("=" * 72)
    return "\n".join(lines) + "\n"


def main() -> None:
    """
    入口。
    """
    target = resolve_path(TARGET_LGC_PATH)
    if target is None:
        logger.error("TARGET_LGC_PATH is not set")
        return

    lgc_files = collect_lgc_files(target)
    if not lgc_files:
        logger.error(
            "No .lgc found at TARGET_LGC_PATH (file or directory): %s",
            TARGET_LGC_PATH,
        )
        return

    if target.is_file():
        target_label = str(target)
    else:
        target_label = "%s (%d .lgc file(s))" % (target, len(lgc_files))

    logger.info("Scanning %s", target_label)
    issues = scan_lgc_paths(lgc_files)
    log_issues(issues)

    report = format_report(issues, target_label)
    output_path = resolve_path(OUTPUT_REPORT)
    if output_path is not None:
        output_path.write_text(report, encoding="utf-8")
        logger.info("Report written: %s", output_path)

    print(report)

    error_count = 0
    for issue in issues:
        if issue.severity == ISSUE_ERROR:
            error_count += 1
    if error_count > 0:
        logger.error("Scan finished with %d ERROR(s)", error_count)


if __name__ == "__main__":
    main()
