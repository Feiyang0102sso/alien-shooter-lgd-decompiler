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

    property:
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
    解析大型 LGC 源码文本，将其分割并提取出所有的顶级函数信息。

    参数:
        lgc_content: 大的 .lgc 文件全部文本内容。

    返回:
        解析出的 LgcFunction 对象列表，保持它们在源文件中的物理定义顺序。
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
            # 解析并提取该函数体内的行号范围
            _fill_line_bounds(func_obj)
            functions.append(func_obj)

            # 重置解析状态
            in_func = False
            current_name = ""
            current_lines = []
            start_idx = 0
            brace_depth = 0

    return functions


def decide_segments(functions: list[LgcFunction]) -> dict[str, list[LgcFunction]]:
    """
    依据行号回跳规则将顶级函数列表划分为不同的段（segment）：
    - 第一次行号回跳（next.min_line < prev.max_line）发生之前的所有顶级方法，归为 "export" 公共段。
    - 之后每次发生行号回跳，都将切分为一个新的独立普通段。
    - 不带任何行号的空函数等无行号函数默认继续并入当前被分配的容器中。

    参数:
        functions: 顶层函数 LgcFunction 对象列表。

    返回:
        包含以下键的字典：
        - "export": list[LgcFunction] (公共导出段包含的函数列表)
        - "segments": list[list[LgcFunction]] (每个普通 segment 包含的函数列表)
    """
    segments: dict[str, list] = {"export": [], "segments": []}

    if len(functions) == 0:
        return segments

    has_jumped = False
    current_segment: list[LgcFunction] = []

    # 记录上一个有效含有行号的函数的最大行号
    prev_max = 0

    for func in functions:
        # 如果函数内没有任何行号，我们不引发错误，默认归入当前所处的容器中
        if func.min_line is None or func.max_line is None:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)
            continue

        # 判断是否发生了回跳。回跳规则：当前函数的最小行号小于前一有效函数的最大行号
        if func.min_line < prev_max:
            has_jumped = True
            # 如果之前的普通段列表已经有了内容，则保存为已完成的普通段，并重启新段
            if len(current_segment) > 0:
                segments["segments"].append(current_segment)
            current_segment = [func]
        else:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)

        # 更新有效的前一个最大行号
        prev_max = func.max_line

    # 遍历结束，如果普通段里还有未导出的函数，将其作为最后一个 segment 追加
    if len(current_segment) > 0:
        segments["segments"].append(current_segment)

    return segments


def write_segment_files(
    segments: dict[str, list[LgcFunction]],
    output_dir: Path,
    original_name: str = "main.lgc",
) -> None:
    """
    将从决定段落中切分出来的顶级函数段（export 与 segments）写入指定的输出目录中。

    参数:
        segments: decide_segments 返回的切分后的函数映射字典。
        output_dir: 目标物理输出目录。
        original_name: 最后一个（主入口）段落的文件名。
    """
    # make sure dir exist
    output_dir.mkdir(parents=True, exist_ok=True)

    export_list = segments.get("export", [])
    segment_lists = segments.get("segments", [])

    # 1. first seg write into export.lgc
    if len(export_list) > 0:
        export_file = output_dir / "export.lgc"
        export_lines = []
        export_lines.append("// ==========================================")
        export_lines.append("// file core/export.lgc")
        export_lines.append("// ==========================================")
        export_lines.append("")

        for func in export_list:
            # export_lines.append(
            #     f"// 函数: {func.name} (行号范围: {func.min_line} ~ {func.max_line})"
            # )
            for line in func.lines:
                export_lines.append(line)
            export_lines.append("")

        export_file.write_text("\n".join(export_lines), encoding="utf-8")
        logger.info("Successfully wrote export functions to: %s", export_file)

    # 2. write into each segment_XX.lgc
    num_segs = len(segment_lists)
    for idx, seg in enumerate(segment_lists):
        # 最后一个 segment 使用原来的名字，不使用 segment_xx.lgc
        if idx == num_segs - 1:
            if original_name.lower().endswith(".lgc"):
                seg_file_name = original_name
            else:
                seg_file_name = f"{original_name}.lgc"
        else:
            seg_file_name = f"segment_{idx + 1:02d}.lgc"

        seg_file = output_dir / seg_file_name

        # 生成防重复引用的唯一 sentinel 宏名
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

