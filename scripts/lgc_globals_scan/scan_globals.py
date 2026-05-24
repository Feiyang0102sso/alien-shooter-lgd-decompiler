"""
scan_globals.py

Scan decompiled .lgc globals:
  - stats for names that appear in exactly 1 file
  - list names that appear in >= 2 files
  - WARNING when same name has differing declarations
"""

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

from lgd_tool.logger import logger

from global_parser import GlobalDecl, parse_globals_from_lgc


DEFAULT_TARGET_PATH = Path(r"E:\aa internet download\ASFree_4.5.3_win\maps")


@dataclass
class NameGroup:
    """All declarations sharing one global variable name."""

    name: str
    occurrences: list[GlobalDecl]

    @property
    def file_count(self) -> int:
        """Number of distinct .lgc files containing this name."""
        paths: set[Path] = set()
        for occ in self.occurrences:
            paths.add(occ.file_path)
        return len(paths)

    @property
    def variant_texts(self) -> list[str]:
        """Distinct normalized declaration texts."""
        seen: set[str] = set()
        texts: list[str] = []
        for occ in self.occurrences:
            key = occ.normalized_line
            if key in seen:
                continue
            seen.add(key)
            texts.append(key)
        return texts

    @property
    def has_value_conflict(self) -> bool:
        """True when the same name has more than one distinct declaration."""
        return len(self.variant_texts) > 1


def resolve_target(raw: Optional[str]) -> Path:
    if raw is None or raw.strip() == "":
        return DEFAULT_TARGET_PATH.expanduser().resolve()
    return Path(raw).expanduser().resolve()


def collect_lgc_files(target: Path) -> list[Path]:
    if target.is_file():
        return [target]
    if not target.is_dir():
        logger.error("[GLOBAL-SCAN] Path not found: %s", target)
        return []
    files: list[Path] = []
    for path in sorted(target.rglob("*.lgc")):
        if path.is_file():
            files.append(path)
    return files


def rel_path(file_path: Path, root: Path) -> str:
    try:
        return str(file_path.relative_to(root))
    except ValueError:
        return str(file_path)


def scan_all(lgc_files: list[Path]) -> dict[str, NameGroup]:
    """Parse all files and group declarations by variable name."""
    by_name: dict[str, list[GlobalDecl]] = defaultdict(list)
    for lgc_path in lgc_files:
        for decl in parse_globals_from_lgc(lgc_path):
            by_name[decl.name].append(decl)

    groups: dict[str, NameGroup] = {}
    for name in sorted(by_name.keys()):
        groups[name] = NameGroup(name=name, occurrences=by_name[name])
    return groups


def log_value_conflict(group: NameGroup, root: Path) -> None:
    """Emit WARNING for same name with different declaration texts."""
    logger.warning(
        "[GLOBAL-SCAN] name=%s file_count=%d variants=%d",
        group.name,
        group.file_count,
        len(group.variant_texts),
    )
    variant_idx = 0
    for text in group.variant_texts:
        variant_idx += 1
        logger.warning("[GLOBAL-SCAN]   variant %d: %s", variant_idx, text)
        for occ in group.occurrences:
            if occ.normalized_line != text:
                continue
            logger.warning(
                "[GLOBAL-SCAN]     %s:%d",
                rel_path(occ.file_path, root),
                occ.line_no,
            )


def build_report(
    root: Path,
    groups: dict[str, NameGroup],
    file_count: int,
) -> str:
    """Build text report: stats for once-only, list for multi-file names."""
    once: list[NameGroup] = []
    multi: list[NameGroup] = []
    conflicts: list[NameGroup] = []

    for group in groups.values():
        if group.file_count == 1:
            once.append(group)
        else:
            multi.append(group)
            if group.has_value_conflict:
                conflicts.append(group)

    once.sort(key=lambda g: g.name)
    multi.sort(key=lambda g: g.name)

    lines: list[str] = []
    lines.append("LGC Global Scan")
    lines.append("target: %s" % root)
    lines.append("lgc_files: %d" % file_count)
    lines.append("unique_names: %d" % len(groups))
    lines.append("")
    lines.append("--- count=1 (single file only) ---")
    lines.append("count: %d" % len(once))
    lines.append("")
    lines.append("--- count>=2 (listed below) ---")
    lines.append("count: %d" % len(multi))
    lines.append("value_conflicts: %d (see WARNING in log)" % len(conflicts))
    lines.append("")

    if not multi:
        lines.append("(none)")
        return "\n".join(lines)

    for group in multi:
        canonical = group.variant_texts[0]
        tag = "OK"
        if group.has_value_conflict:
            tag = "CONFLICT"
        lines.append(
            "[%s] %s  files=%d  decl=%s"
            % (tag, group.name, group.file_count, canonical)
        )

    return "\n".join(lines)


def main(argv: Optional[list[str]] = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(description="Scan LGC global variables.")
    parser.add_argument("target", nargs="?", help="File or directory")
    parser.add_argument("-o", "--output", help="Write report to file")
    args = parser.parse_args(argv)

    root = resolve_target(args.target)
    logger.info("[GLOBAL-SCAN] target=%s", root)

    lgc_files = collect_lgc_files(root)
    if not lgc_files:
        logger.error("[GLOBAL-SCAN] no .lgc files")
        return 1

    logger.info("[GLOBAL-SCAN] files=%d", len(lgc_files))
    groups = scan_all(lgc_files)

    once_count = 0
    multi_count = 0
    conflict_count = 0

    for group in groups.values():
        if group.file_count == 1:
            once_count += 1
        else:
            multi_count += 1
            if group.has_value_conflict:
                conflict_count += 1
                log_value_conflict(group, root)

    report = build_report(root, groups, len(lgc_files))
    print(report)

    if args.output:
        out = Path(args.output).expanduser().resolve()
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        logger.info("[GLOBAL-SCAN] report=%s", out)

    logger.info(
        "[GLOBAL-SCAN] done names_once=%d names_multi=%d conflicts=%d",
        once_count,
        multi_count,
        conflict_count,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
