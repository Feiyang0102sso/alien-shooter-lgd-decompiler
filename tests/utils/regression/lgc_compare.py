"""
LGC regression compare helpers.

Parse function blocks after ``// Function Implementations`` and diff line-by-line.
"""

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from tests.conftest import REGRESSION_LGC_DIR

FUNCTION_IMPL_MARKER = "// Function Implementations"
CONFIG_FILE_NAME = "config.json"

# Top-level function signature only: must start at column 0 (not indented if/Action/...)
_SIGNATURE_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(")


@dataclass
class LgcLine:
    """One source line inside a function block."""

    file_line: int
    text: str


@dataclass
class FunctionDiff:
    """One differing line inside a function body."""

    function_name: str
    expected_file_line: int | None
    actual_file_line: int | None
    expected_line: str
    actual_line: str


@dataclass
class CompareResult:
    """Outcome of comparing two LGC texts by function."""

    passed: bool
    function_diffs: list[FunctionDiff] = field(default_factory=list)
    missing_functions: list[str] = field(default_factory=list)
    extra_functions: list[str] = field(default_factory=list)
    message: str = ""


def load_max_diff_lines(basename: str, default: int = 0) -> int:
    """
    Read per-case ``max_diff_lines`` from optional ``regression_lgc/config.json``.

    ``basename`` is the stem including prefix, e.g. ``regression_tutorial_00``.
    """
    config_path = REGRESSION_LGC_DIR / CONFIG_FILE_NAME
    if not config_path.exists():
        return default

    try:
        raw = config_path.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return default

    if not isinstance(data, dict):
        return default

    entry = data.get(basename)
    if entry is None:
        return default

    if isinstance(entry, dict):
        value = entry.get("max_diff_lines", default)
    else:
        value = default

    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _normalize_line(line: str) -> str:
    """Strip trailing whitespace; keep empty lines as empty."""
    return line.rstrip()


def _function_name_from_signature(signature_line: str) -> str:
    """Extract identifier before '(' from the first line of a function block."""
    stripped = signature_line.strip()
    paren_index = stripped.find("(")
    if paren_index == -1:
        return stripped
    return stripped[:paren_index].strip()


def _is_separator_comment(line: str) -> bool:
    """True for decorative ``// ===`` lines between functions."""
    stripped = line.strip()
    if not stripped.startswith("//"):
        return False
    body = stripped[2:].strip()
    if not body:
        return False
    return set(body) <= {"=", "-"}


def _find_implementation_start(all_lines: list[str]) -> int | None:
    """Return 0-based index of the ``Function Implementations`` marker line."""
    for index, line in enumerate(all_lines):
        if FUNCTION_IMPL_MARKER in line:
            return index
    return None


def _append_block_line(
    block_lines: list[LgcLine],
    all_lines: list[str],
    line_index: int,
) -> None:
    """Append one line with 1-based file line number."""
    raw_line = all_lines[line_index]
    entry = LgcLine(
        file_line=line_index + 1,
        text=_normalize_line(raw_line),
    )
    block_lines.append(entry)


def parse_lgc_functions(lgc_text: str) -> dict[str, list[LgcLine]]:
    """
    Parse function blocks from decompiled LGC text.

    Only the region after ``// Function Implementations`` is parsed.
    Keys are function names; values are lines with **file-wide** 1-based line numbers.
    """
    all_lines = lgc_text.splitlines()
    start_index = _find_implementation_start(all_lines)
    if start_index is None:
        return {}

    functions = {}
    index = start_index

    while index < len(all_lines):
        line = all_lines[index]
        if _SIGNATURE_RE.match(line):
            break
        index = index + 1

    while index < len(all_lines):
        line = all_lines[index]
        if not _SIGNATURE_RE.match(line):
            index = index + 1
            continue

        block_lines = []
        _append_block_line(block_lines, all_lines, index)
        index = index + 1

        brace_depth = line.count("{") - line.count("}")

        while brace_depth <= 0 and index < len(all_lines):
            open_line = all_lines[index]
            if _SIGNATURE_RE.match(open_line):
                break
            _append_block_line(block_lines, all_lines, index)
            brace_depth = brace_depth + open_line.count("{") - open_line.count("}")
            index = index + 1

        while brace_depth > 0 and index < len(all_lines):
            body_line = all_lines[index]
            if _SIGNATURE_RE.match(body_line):
                break
            _append_block_line(block_lines, all_lines, index)
            brace_depth = brace_depth + body_line.count("{") - body_line.count("}")
            index = index + 1

        func_name = _function_name_from_signature(block_lines[0].text)
        functions[func_name] = block_lines

        while index < len(all_lines):
            skip_line = all_lines[index]
            if skip_line.strip() == "":
                index = index + 1
                continue
            if _is_separator_comment(skip_line):
                index = index + 1
                continue
            break

    return functions


def compare_lgc_by_function(
    expected_text: str,
    actual_text: str,
    max_diff_lines: int = 0,
) -> CompareResult:
    """
    Compare two LGC files function-by-function (order-independent).

    ``max_diff_lines``: allow up to this many differing lines total; default ``0`` means
    any mismatch fails.
    """
    expected_funcs = parse_lgc_functions(expected_text)
    actual_funcs = parse_lgc_functions(actual_text)

    expected_names = set(expected_funcs.keys())
    actual_names = set(actual_funcs.keys())

    missing = sorted(expected_names - actual_names)
    extra = sorted(actual_names - expected_names)

    function_diffs = []
    common_names = sorted(expected_names & actual_names)

    for func_name in common_names:
        expected_lines = expected_funcs[func_name]
        actual_lines = actual_funcs[func_name]
        max_len = max(len(expected_lines), len(actual_lines))

        for line_index in range(max_len):
            expected_entry = None
            actual_entry = None
            if line_index < len(expected_lines):
                expected_entry = expected_lines[line_index]
            if line_index < len(actual_lines):
                actual_entry = actual_lines[line_index]

            expected_text_line = ""
            actual_text_line = ""
            expected_file_line = None
            actual_file_line = None

            if expected_entry is not None:
                expected_text_line = expected_entry.text
                expected_file_line = expected_entry.file_line
            if actual_entry is not None:
                actual_text_line = actual_entry.text
                actual_file_line = actual_entry.file_line

            if expected_text_line != actual_text_line:
                function_diffs.append(
                    FunctionDiff(
                        function_name=func_name,
                        expected_file_line=expected_file_line,
                        actual_file_line=actual_file_line,
                        expected_line=expected_text_line,
                        actual_line=actual_text_line,
                    )
                )

    total_mismatches = len(missing) + len(extra) + len(function_diffs)
    allowed = max_diff_lines
    passed = total_mismatches <= allowed

    message = format_compare_failure(
        function_diffs=function_diffs,
        missing_functions=missing,
        extra_functions=extra,
        max_diff_lines=max_diff_lines,
        total_mismatches=total_mismatches,
    )

    return CompareResult(
        passed=passed,
        function_diffs=function_diffs,
        missing_functions=missing,
        extra_functions=extra,
        message=message,
    )


def _format_file_line(line_number: int | None) -> str:
    """Format 1-based file line for reports; missing side shows ``-``."""
    if line_number is None:
        return "-"
    return str(line_number)


def format_compare_failure(
    function_diffs: list[FunctionDiff],
    missing_functions: list[str],
    extra_functions: list[str],
    max_diff_lines: int,
    total_mismatches: int,
    case_name: str = "",
    work_dir: Path | None = None,
    limit: int = 20,
) -> str:
    """Build a human-readable failure report (pytest assertion text)."""
    lines = []

    if case_name:
        lines.append(f"FAILED {case_name}")

    if missing_functions:
        lines.append(f"  missing functions ({len(missing_functions)}): {', '.join(missing_functions)}")

    if extra_functions:
        lines.append(f"  extra functions ({len(extra_functions)}): {', '.join(extra_functions)}")

    shown = 0
    for diff in function_diffs:
        if shown >= limit:
            lines.append(f"  ... and {len(function_diffs) - limit} more line diffs")
            break
        lines.append(f"  function {diff.function_name}")
        exp_no = _format_file_line(diff.expected_file_line)
        act_no = _format_file_line(diff.actual_file_line)
        lines.append(f"    file line {exp_no} (expected): {diff.expected_line}")
        lines.append(f"    file line {act_no} (actual):   {diff.actual_line}")
        shown = shown + 1

    lines.append(
        f"  total mismatches: {total_mismatches}, max_diff_lines: {max_diff_lines}"
    )

    if work_dir is not None:
        lines.append(f"work_dir: {work_dir}")

    return "\n".join(lines)
