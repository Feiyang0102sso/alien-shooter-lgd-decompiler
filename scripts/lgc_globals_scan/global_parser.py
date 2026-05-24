"""
global_parser.py

Parse global variable declarations from decompiled LGC source files.
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


GLOBAL_SECTION_START = "// --- Global Variables ---"
FUNCTION_SECTION_START = "// Function Implementations"
SECTION_DIVIDER = "// =========================================="

# int/string global with optional array and initializer.
# Does not match extern lines.
GLOBAL_DECL_PATTERN = re.compile(
    r"^\s*(?:static\s+)?(?P<type>int|string)\s+"
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*"
    r"(?P<array>\[[^\]]*\])?\s*"
    r"(?P<init>=\s*.+?)?\s*;\s*(?://.*)?$"
)


@dataclass
class GlobalDecl:
    """One global variable declaration found in an LGC file."""

    name: str
    type_name: str
    line_no: int
    raw_line: str
    file_path: Path
    normalized_line: str = ""


def normalize_decl_text(raw_line: str) -> str:
    """
    Normalize declaration text for loose comparison.

    Removes static prefix and collapses whitespace so decompiler formatting
    differences (e.g. with/without static) can be distinguished from real
    init-value conflicts.
    """
    text = raw_line.strip()
    if text.startswith("static "):
        text = text[len("static ") :]
    if text.startswith("static\t"):
        text = text[len("static\t") :]
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _strip_inline_comment(line: str) -> str:
    """Remove trailing // comment for matching."""
    comment_idx = line.find("//")
    if comment_idx >= 0:
        return line[:comment_idx].rstrip()
    return line.rstrip()


def _is_global_decl_line(line: str) -> bool:
    """Return True when the line looks like a global variable declaration."""
    text = _strip_inline_comment(line)
    if text == "":
        return False
    if text.startswith("extern "):
        return False
    if text.startswith("#"):
        return False
    match = GLOBAL_DECL_PATTERN.match(line)
    if match is None:
        return False
    return True


def _parse_global_line(line: str, line_no: int, file_path: Path) -> Optional[GlobalDecl]:
    """Parse one line into GlobalDecl when it is a global declaration."""
    if not _is_global_decl_line(line):
        return None

    match = GLOBAL_DECL_PATTERN.match(line)
    if match is None:
        return None

    name = match.group("name")
    type_name = match.group("type")
    raw = line.rstrip()
    return GlobalDecl(
        name=name,
        type_name=type_name,
        line_no=line_no,
        raw_line=raw,
        file_path=file_path,
        normalized_line=normalize_decl_text(raw),
    )


def _find_global_section_range(lines: list[str]) -> Optional[tuple[int, int]]:
    """
    Find line index range [start, end) of the decompiler global variables block.

    Returns:
        (start_index, end_index) or None when the marker section is missing.
    """
    start_idx = -1
    for idx, line in enumerate(lines):
        if GLOBAL_SECTION_START in line:
            start_idx = idx + 1
            break

    if start_idx < 0:
        return None

    end_idx = len(lines)
    for idx in range(start_idx, len(lines)):
        line = lines[idx].strip()
        if line == SECTION_DIVIDER:
            end_idx = idx
            break
        if FUNCTION_SECTION_START in line:
            end_idx = idx
            break

    return start_idx, end_idx


def _find_fallback_global_range(lines: list[str]) -> tuple[int, int]:
    """
    Fallback for LGC without decompiler section markers.

    Scan from file start until the first top-level function signature.
    """
    func_pattern = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*\s*\([^)]*\)\s*$")
    reserved = ("if", "while", "for", "switch", "else", "iff", "extern")

    end_idx = len(lines)
    for idx, line in enumerate(lines):
        match = func_pattern.match(line)
        if match is None:
            continue
        name = line.split("(", maxsplit=1)[0].strip()
        if name in reserved:
            continue
        end_idx = idx
        break

    return 0, end_idx


def parse_globals_from_lgc(lgc_path: Path) -> list[GlobalDecl]:
    """
    Extract global variable declarations from one LGC file.

    Args:
        lgc_path: Path to a .lgc file.

    Returns:
        List of GlobalDecl entries in source order.
    """
    text = lgc_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()

    section_range = _find_global_section_range(lines)
    if section_range is None:
        start_idx, end_idx = _find_fallback_global_range(lines)
    else:
        start_idx, end_idx = section_range

    results: list[GlobalDecl] = []
    for idx in range(start_idx, end_idx):
        line_no = idx + 1
        line = lines[idx]
        decl = _parse_global_line(line, line_no, lgc_path)
        if decl is not None:
            results.append(decl)

    return results
