"""
scripts/endless_loop_detect/inject_log_per_method.py

在反编译得到的 LGC 中，为每个顶层方法开头插入 Log 调用，用于 endless loop 逐方法排查。

形如:
Log("ENDLESS LOOP DETECTING, main.lgc generateTimeOfDayGamma()", 2 )
    //等级一律用2级 ENDLESS LOOP DETECTING 为统一前缀
    //main.lgc 获取文件名 generateTimeOfDayGamma() 获取对应的方法名
"""

import re
import shutil
from operator import itemgetter
from pathlib import Path
from typing import Optional, Union

from lgd_tool.logger import logger

# ========== 硬编码路径（按需修改，str 或 Path 均可） ==========
TARGET_LGC_DIR: Union[str, Path] = Path(
    r"E:\aa internet download\ASFree_4.5.3_win\maps"
)

# ========== Log 参数（与验证文档一致，便于统一切换） ==========
LOG_ERROR = 2
LOG_WARNING = 3
LOG_INFO = 4
LOG_DEBUG = 5

# 插入 Log 时使用的等级（文档要求一律 2）
LOG_LEVEL = LOG_ERROR

LOG_PREFIX = "ENDLESS LOOP DETECTING"
DETECT_MARKER = LOG_PREFIX

# True：先备份为 .lgc.bak 再写回；False：直接覆盖
CREATE_BACKUP = True

# True：只统计不写文件
DRY_RUN = False

# ========== 解析用正则 ==========
# 顶层函数签名：行首无缩进，形如 funcName(int a, int b = 0)
FUNCTION_SIGNATURE_PATTERN = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)\s*$"
)

# 方法体内的局部变量声明（插入 Log 须在其后）
LOCAL_DECLARATION_PATTERN = re.compile(
    r"^\s+(?:(?:int|string|bool|real)\s+\w+.*?;)\s*$"
)

# 非函数名的 C/LGC 关键字（行首形如函数调用，需排除）
RESERVED_KEYWORDS = frozenset(
    {
        "if",
        "while",
        "for",
        "switch",
        "else",
        "return",
        "extern",
        "iff",
        "break",
        "continue",
    }
)


def is_function_signature_line(line: str) -> Optional[re.Match]:
    """
    判断是否为顶层函数签名行（列 0，下一行通常为 '{'）。
    """
    match = FUNCTION_SIGNATURE_PATTERN.match(line)
    if match is None:
        return None
    name = match.group(1)
    if name in RESERVED_KEYWORDS:
        return None
    return match


def find_opening_brace_line_index(lines: list[str], signature_index: int) -> Optional[int]:
    """
    在签名行之后查找函数体开头的 '{' 行号。
    支持签名与 '{' 同行：func() { 或分两行。
    """
    signature_line = lines[signature_index]
    stripped = signature_line.rstrip()
    if stripped.endswith("{"):
        return signature_index

    index = signature_index + 1
    while index < len(lines):
        text = lines[index].strip()
        if text == "":
            index += 1
            continue
        if text == "{":
            return index
        break
    return None


def find_log_insert_line_index(lines: list[str], brace_index: int) -> int:
    """
    在 '{' 之后跳过空行与局部变量声明，返回 Log 应插入的行号（0-based）。
    """
    index = brace_index + 1
    while index < len(lines):
        line = lines[index]
        if line.strip() == "":
            index += 1
            continue
        if LOCAL_DECLARATION_PATTERN.match(line):
            index += 1
            continue
        break
    return index


def already_has_detect_log(lines: list[str], insert_index: int) -> bool:
    """
    插入点附近是否已有 endless loop 检测 Log（避免重复运行脚本）。
    """
    scan_start = max(0, insert_index - 1)
    scan_end = min(len(lines), insert_index + 4)
    for idx in range(scan_start, scan_end):
        if DETECT_MARKER in lines[idx]:
            return True
    return False


def build_log_line(file_name: str, function_name: str) -> str:
    """
    生成单条 Log 语句，缩进与反编译体一致（4 空格）。
    """
    message = f'{LOG_PREFIX}, {file_name} {function_name}()'
    return f'    Log("{message}", {LOG_LEVEL});'


def process_lgc_file(lgc_path: Path) -> tuple[int, int]:
    """
    处理单个 LGC 文件。

    Returns:
        (插入条数, 跳过条数因已存在检测 Log)
    """
    text = lgc_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    file_name = lgc_path.name

    insertions: list[tuple[int, str]] = []
    skipped_existing = 0

    line_index = 0
    while line_index < len(lines):
        raw_line = lines[line_index]
        # 去掉行尾换行再匹配，保留原 keepends 写回
        content_line = raw_line.rstrip("\r\n")

        match = is_function_signature_line(content_line)
        if match is None:
            line_index += 1
            continue

        function_name = match.group(1)
        brace_index = find_opening_brace_line_index(lines, line_index)
        if brace_index is None:
            line_index += 1
            continue

        insert_index = find_log_insert_line_index(lines, brace_index)
        if already_has_detect_log(lines, insert_index):
            skipped_existing += 1
            line_index = brace_index + 1
            continue

        log_line = build_log_line(file_name, function_name)
        # 保持与原文件一致的换行符
        if raw_line.endswith("\r\n"):
            newline = "\r\n"
        elif raw_line.endswith("\n"):
            newline = "\n"
        else:
            newline = "\n"
        insertions.append((insert_index, log_line + newline))

        line_index = brace_index + 1

    if not insertions:
        logger.info(
            "No new Log lines for %s (skipped_existing=%d)",
            lgc_path,
            skipped_existing,
        )
        return 0, skipped_existing

    # 从后往前插入，避免行号偏移
    insertions.sort(key=itemgetter(0), reverse=True)
    for insert_index, log_line in insertions:
        lines.insert(insert_index, log_line)

    inserted_count = len(insertions)
    logger.info(
        "Will inject %d Log calls into %s (skipped_existing=%d)",
        inserted_count,
        lgc_path,
        skipped_existing,
    )

    if DRY_RUN:
        return inserted_count, skipped_existing

    if CREATE_BACKUP:
        backup_path = lgc_path.with_suffix(lgc_path.suffix + ".bak")
        shutil.copy2(lgc_path, backup_path)
        logger.info("Backup created: %s", backup_path)

    lgc_path.write_text("".join(lines), encoding="utf-8")
    return inserted_count, skipped_existing


def resolve_target_dir(target_dir: Union[str, Path]) -> Path:
    """
    将配置中的路径统一转为 Path（支持 str 与 Path）。
    """
    return Path(target_dir).expanduser()


def collect_lgc_files(target_dir: Union[str, Path]) -> list[Path]:
    """
    收集目录下所有 .lgc 文件（递归子目录）。
    """
    target_dir = resolve_target_dir(target_dir)
    if not target_dir.exists():
        return []
    result: list[Path] = []
    for path in sorted(target_dir.rglob("*.lgc")):
        if path.is_file():
            result.append(path)
    return result


def main() -> None:
    """
    入口：处理 TARGET_LGC_DIR 下全部 .lgc。
    """
    target_dir = resolve_target_dir(TARGET_LGC_DIR)
    logger.info("Target LGC directory: %s", target_dir)
    logger.info("DRY_RUN=%s CREATE_BACKUP=%s LOG_LEVEL=%d", DRY_RUN, CREATE_BACKUP, LOG_LEVEL)

    if not target_dir.is_dir():
        logger.error("Target path does not exist or is not a directory: %s", target_dir)
        return

    lgc_files = collect_lgc_files(target_dir)
    if not lgc_files:
        logger.error("No .lgc files found under %s", target_dir)
        return

    total_inserted = 0
    total_skipped = 0
    for lgc_path in lgc_files:
        inserted, skipped = process_lgc_file(lgc_path)
        total_inserted += inserted
        total_skipped += skipped

    logger.info(
        "Done. files=%d inserted=%d skipped_existing=%d dry_run=%s",
        len(lgc_files),
        total_inserted,
        total_skipped,
        DRY_RUN,
    )


if __name__ == "__main__":
    main()
