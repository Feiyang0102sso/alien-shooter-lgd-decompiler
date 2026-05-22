"""
scripts/endless_loop_detect/split_loop_log.py

将混合的检测日志按 LGC 文件名拆成多个 .log，便于手动分析。
例如 main.lgc 相关行 → main.log，foo.lgc 相关行 → foo.log。

只处理 ENDLESS LOOP DETECTING 行；其余内容暂不输出。
"""

import re
from pathlib import Path
from typing import Optional, Union

from lgd_tool.logger import logger

# ========== 硬编码路径（按需修改，str 或 Path 均可） ==========
# 输入：单个 .log / .ini / .txt
INPUT_LOG_FILE: Union[str, Path] = (
    r"E:\aa internet download\ASFree_4.5.3_win\logs\AlienShooterGold.log"
)

# 输出目录；None 表示与输入文件同目录
OUTPUT_DIR: Union[str, Path, None] = None

# inject_log 写入格式（与 inject_log_per_method.py 一致）
DETECT_LINE_PATTERN = re.compile(
    r"^\s*\[(?P<level>[EWID])\]\s+"
    r"(?P<time>\d{2}:\d{2}:\d{2}\.\d+)"
    r"\s+-\s+\[(?P<thread>[^\]]+)\]\s+"
    r"SCRIPT:\s+ENDLESS LOOP DETECTING,\s+"
    r"(?P<lgc_file>[^\s]+\.lgc)\s+"
    r"(?P<func>\w+)\(\)\s*$"
)


def resolve_path(value: Union[str, Path, None]) -> Optional[Path]:
    """将配置路径转为 Path。"""
    if value is None:
        return None
    return Path(value).expanduser()


def lgc_name_to_output_name(lgc_file_name: str) -> str:
    """
    main.lgc → main.log（去掉 .lgc 后缀，换成 .log）。
    """
    stem = Path(lgc_file_name).stem
    return stem + ".log"


def split_log_by_lgc_file(input_path: Path, output_dir: Path) -> dict[str, int]:
    """
    读取混合日志，按 .lgc 文件名归类写入多个 .log。

    同一文件的所有行按在原文中的出现顺序保留（第一行到最后一行）。

    Returns:
        {输出文件名: 行数}
    """
    buckets: dict[str, list[str]] = {}
    text = input_path.read_text(encoding="utf-8", errors="replace")
    matched_total = 0

    for raw_line in text.splitlines():
        line = raw_line.strip()
        match = DETECT_LINE_PATTERN.match(line)
        if match is None:
            continue
        matched_total += 1
        lgc_file = match.group("lgc_file")
        out_name = lgc_name_to_output_name(lgc_file)
        if out_name not in buckets:
            buckets[out_name] = []
        # 保留原始行（含可能的前后空白），便于对照
        buckets[out_name].append(raw_line)

    if matched_total == 0:
        logger.warning("No ENDLESS LOOP DETECTING lines found in %s", input_path)
        return {}

    output_dir.mkdir(parents=True, exist_ok=True)
    written_counts: dict[str, int] = {}

    for out_name in sorted(buckets.keys()):
        lines = buckets[out_name]
        out_path = output_dir / out_name
        body = "\n".join(lines)
        if body:
            body += "\n"
        out_path.write_text(body, encoding="utf-8")
        written_counts[out_name] = len(lines)
        logger.info("Wrote %d lines -> %s", len(lines), out_path)

    return written_counts


def main() -> None:
    """
    入口：拆分单个日志文件。
    """
    input_path = resolve_path(INPUT_LOG_FILE)
    if input_path is None or not input_path.is_file():
        logger.error("INPUT_LOG_FILE not found: %s", INPUT_LOG_FILE)
        return

    out_dir = resolve_path(OUTPUT_DIR)
    if out_dir is None:
        out_dir = input_path.parent

    logger.info("Input log: %s", input_path)
    logger.info("Output dir: %s", out_dir)

    counts = split_log_by_lgc_file(input_path, out_dir)
    if not counts:
        return

    logger.info("Done. %d file(s): %s", len(counts), ", ".join(sorted(counts.keys())))


if __name__ == "__main__":
    main()
