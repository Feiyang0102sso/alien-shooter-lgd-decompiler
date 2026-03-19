"""
/refine_data_prepare/find_constants_usage.py
用于从指定的 .h 文件中提取宏定义，并在整个项目的 .lgc 文件中进行全量匹配搜索。
搜索结果将输出为特定格式的 .ini 文件，每次运行前自动清空。
"""

import re
from pathlib import Path
from lgd_tool.logger import logger

# --- 环境初始化 ---
CURRENT_DIR = Path(__file__).resolve().parent


# --- 配置区 ---
# 宏定义来源文件 (.h)
HEADER_FILE_PATH = CURRENT_DIR / "data" / "export_AS2TL_Beta.lgc"
# 要扫描的项目目录 (包含所有的 .lgc 文件)
PROJECT_LGC_DIR = Path(r"D:\A-GameCenter\alien shooter\as2 tl lgc")
# 搜索结果输出路径 (.ini)
OUTPUT_INI_PATH = CURRENT_DIR / "output" /"constants_usage_results.ini"

# 支持的编码列表 (顺序很重要：先尝试严格的 utf-8，失败再回退到 windows-1251)
SUPPORTED_ENCODINGS = ['utf-8', 'windows-1251']

# 解析 #define 的正则：仅抓取宏名称
# 支持普通的 #define NAME val 以及带参数的宏 #define NAME(x) val
DEFINE_PATTERN = re.compile(r'^\s*#define\s+(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)')


def safe_read_lines(file_path: Path) -> list:
    """
    智能读取文件内容：自动尝试配置的多种编码格式。
    """
    for enc in SUPPORTED_ENCODINGS:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return f.readlines()
        except UnicodeDecodeError:
            continue  # 当前编码失败，尝试下一种

    # 如果所有常规编码都失败了，强制用 utf-8 读取并忽略错误字符，保证程序不崩溃
    logger.warning(f"无法精准识别文件编码，将忽略乱码强制读取: {file_path.name}")
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.readlines()


def extract_constants(header_path: Path) -> list:
    """
    从 .h 文件中提取所有的宏名称。
    """
    constants = set()
    if not header_path.exists():
        logger.error_and_stop(f"找不到头文件: {header_path}")
        return []

    lines = safe_read_lines(header_path)
    for line in lines:
        match = DEFINE_PATTERN.search(line)
        if match:
            name = match.group('name')
            constants.add(name)

    logger.info(f"从 {header_path.name} 中成功提取了 {len(constants)} 个宏定义。")
    return list(constants)


def scan_usages(lgc_dir: Path, constants: list) -> tuple:
    """
    在指定目录下的所有 .lgc 文件中扫描常量的使用情况。
    返回 (结果字典, 扫描的文件总数)
    """
    if not lgc_dir.exists() or not lgc_dir.is_dir():
        logger.error_and_stop(f"指定的 LGC 项目目录不存在或无效: {lgc_dir}")

        # 遍历所有文件，并强制忽略后缀名的大小写 (支持 .LGC, .lgc, .Lgc 等)
    lgc_files = [
        f for f in lgc_dir.rglob("*")
        if f.is_file() and f.suffix.lower() == '.lgc'
        ]

    total_files = len(lgc_files)
    # print(lgc_files)
    logger.info(f"找到 {total_files} 个 .lgc 文件，开始极速扫描...")

    # 初始化结果字典: { "MACRO_NAME": { Path(file): [(line_num, line_text), ...] } }
    results = {c: {} for c in constants}

    # 预编译正则边界，防止类似 EQUIPMENT_MAX 匹配到 EQUIPMENT_MAX_BUY_AMMO
    const_patterns = {c: re.compile(r'\b' + re.escape(c) + r'\b') for c in constants}

    for lgc_file in lgc_files:
        lines = safe_read_lines(lgc_file)

        for line_num, line in enumerate(lines, 1):
            line_str = line.strip()
            if not line_str:
                continue

            for const, pattern in const_patterns.items():
                # 性能优化：先用 `in` 快速判断，命中后再用正则严格校验边界
                if const in line_str:
                    if pattern.search(line_str):
                        if lgc_file not in results[const]:
                            results[const][lgc_file] = []
                        results[const][lgc_file].append((line_num, line_str))

    return results, total_files


def write_results_to_ini(results: dict, total_files: int, output_path: Path):
    """
    将扫描结果以指定的格式写入到 .ini 文件中。每次写入前覆盖。
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    sorted_constants = sorted(results.keys())

    # mode='w' 会在每次打开时自动清空文件
    with open(output_path, 'w', encoding='utf-8') as f:
        for const in sorted_constants:
            file_matches_dict = results[const]

            total_matches = sum(len(matches) for matches in file_matches_dict.values())
            file_count = len(file_matches_dict)

            # 标题行
            f.write(
                f'搜索 "{const}" ({file_count} 个文件中匹配到 {total_matches} 次，总计查找 {total_files} 个文件) [普通]\n')

            if file_count == 0:
                f.write("\n")
                continue

            # 详情行
            for file_path, matches in file_matches_dict.items():
                f.write(f'  {file_path.resolve()} (匹配 {len(matches)} 次)\n')
                for line_num, line_text in matches:
                    f.write(f'\t行 {line_num}:    {line_text}\n')

            f.write('\n')

    logger.info(f"结果已成功输出到: {output_path.name}")


if __name__ == "__main__":
    logger.info("=== 开始常量全量搜索 ===")

    # 1. 提取常量
    extracted_constants = extract_constants(HEADER_FILE_PATH)

    if extracted_constants:
        # 2. 扫描使用情况
        scan_results, scanned_total = scan_usages(PROJECT_LGC_DIR, extracted_constants)

        # 3. 输出报告
        write_results_to_ini(scan_results, scanned_total, OUTPUT_INI_PATH)

    logger.info("=== 搜索任务结束 ===")