"""
func_splitter.py

core in splitting the large LGC into different segments
based on next.min_line < prev.max_line algorithm
first segment belong to export.lgc
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from lgd_tool.logger import logger

# match such as MyFunction(int a, string b)。
# well.... it seems 1150_15() can be defined
# though it seems it was a bug
FUNC_DECL_PATTERN = re.compile(r"^([A-Za-z0-9_]+)\s*\([^)]*\)\s*$")

# exclude if, while, for and other control flow
# eg while(x) {}
RESERVED_KEYWORDS = frozenset(
    ("if", "else", "iff", "while", "for", "extern")
)

# match line num "// --- Line 965 ---" or "// --- Line  965 ---"
LINE_COMMENT_PATTERN = re.compile(r"//\s*---\s*Line\s+(\d+)\s*---")


@dataclass
class LgcFunction:
    """
    Data structure for storing LGC function datas

    Attributes:
        name: func name
        start_line_idx: index from original LGC, from 0
        lines: func lines
        min_line: Min LINE_NUM in func, none means empty func
        max_line: Max LINE_NUM in func, none means empty func
    """

    name: str
    start_line_idx: int
    lines: list[str]
    min_line: Optional[int] = None
    max_line: Optional[int] = None


def _fill_line_bounds(func: LgcFunction) -> None:
    """
    read LINE_NUM and calculate the Min/Max

    :param func: LgcFunction without line num bound
    """
    found_lines = []
    for line in func.lines:
        match = LINE_COMMENT_PATTERN.search(line)
        if match is not None:
            raw_val = match.group(1)
            int_val = int(raw_val)
            found_lines.append(int_val)

    if len(found_lines) > 0:
        # find min/max
        min_val = found_lines[0]
        max_val = found_lines[0]
        for val in found_lines:
            if val < min_val:
                min_val = val
            if val > max_val:
                max_val = val
        func.min_line = min_val
        func.max_line = max_val
    else:
        func.min_line = None
        func.max_line = None


def parse_lgc_functions(lgc_content: str) -> list[LgcFunction]:
    """
    read big LGC and get the func info

    :param lgc_content: all contents in big LGC

    :return: LgcFunction list, with its original order
    """
    lines = lgc_content.splitlines()
    functions: list[LgcFunction] = []

    in_func = False
    current_name = ""
    current_lines: list[str] = []
    start_idx = 0
    brace_depth = 0

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not in_func:
            match = FUNC_DECL_PATTERN.match(line)
            if match is not None:
                name = match.group(1)
                if name not in RESERVED_KEYWORDS:
                    current_name = name
                    current_lines = [line]
                    start_idx = idx
                    in_func = True
                    brace_depth = 0
            continue

        current_lines.append(line)
        brace_depth += line.count("{")
        brace_depth -= line.count("}")

        if brace_depth <= 0 and stripped == "}":
            func_obj = LgcFunction(
                name=current_name,
                start_line_idx=start_idx,
                lines=current_lines,
            )
            # cal line num bound
            _fill_line_bounds(func_obj)
            functions.append(func_obj)

            # reset status
            in_func = False
            current_name = ""
            current_lines = []
            start_idx = 0
            brace_depth = 0

    return functions


def decide_segments(functions: list[LgcFunction]) -> dict[str, list[LgcFunction]]:
    """
    decided segment based on line num jumps
    - first jump belongs to export
    - the jumps after that belongs to each new segment
    - empty funcs belong to current segment

    :param functions: list of LgcFunction

    :return: - "export": list[LgcFunction] segment that belongs to export
    :return: - "segments": list[list[LgcFunction]] normal segment
    """
    segments: dict[str, list] = {"export": [], "segments": []}

    if len(functions) == 0:
        return segments

    has_jumped = False
    current_segment: list[LgcFunction] = []

    # max line num of last func
    prev_max = 0

    for func in functions:
        # if no line num, it will belong to current segment
        if func.min_line is None or func.max_line is None:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)
            continue

        # decide whether jump happened
        if func.min_line < prev_max:
            has_jumped = True
            # if the segment already have contents, save as current segment and start new
            if len(current_segment) > 0:
                segments["segments"].append(current_segment)
            current_segment = [func]
        else:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)

        # update max line num
        prev_max = func.max_line

    # If there are any unexported functions in segment, append them as the last segment.
    if len(current_segment) > 0:
        segments["segments"].append(current_segment)

    return segments


def write_segment_files(
    segments: dict[str, list[LgcFunction]],
    output_dir: Path,
    original_name: str = "main.lgc",
) -> None:
    """
    write segment into file
    !!!
    functions that belong to export.lgc are now taking handle by the pipeline
    This file no longer write them into file
    !!!

    :param segments: decide_segments, the returned dictionary of split function maps
    :param output_dir: output directory
    :param original_name: last file is the main entrance, keep the original name
    """
    # make sure dir exist
    output_dir.mkdir(parents=True, exist_ok=True)

    segment_lists = segments.get("segments", [])

    # 1. write into each segment_XX.lgc
    num_segs = len(segment_lists)
    for idx, seg in enumerate(segment_lists):
        # last segment will use original name, instead segment_xx.lgc
        if idx == num_segs - 1:
            if original_name.lower().endswith(".lgc"):
                seg_file_name = original_name
            else:
                seg_file_name = f"{original_name}.lgc"
        else:
            seg_file_name = f"segment_{idx:02d}.lgc"

        seg_file = output_dir / seg_file_name

        # introduce sentinels
        macro_name = f"_{seg_file_name.upper().replace('.', '_').replace('-', '_')}_"

        seg_lines = []
        seg_lines.append(f"#ifndef {macro_name}")
        seg_lines.append(f"#define {macro_name} aaa")
        seg_lines.append("")
        seg_lines.append("// ==========================================")
        seg_lines.append(f"// file {seg_file_name}")
        seg_lines.append("// ==========================================")
        seg_lines.append("")

        for func in seg:
            for line in func.lines:
                seg_lines.append(line)
            seg_lines.append("")

        seg_lines.append("#endif")
        seg_lines.append("")

        seg_file.write_text("\n".join(seg_lines), encoding="utf-8")
        logger.info("Successfully wrote segment file with include guard to: %s", seg_file)


