"""
LGC_refiner/refiner.py
LGC Refiner 主入口。
调度 extern 替换和常量替换两个子模块。
"""

import re
from pathlib import Path
from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.LGC_refiner.database_loader import load_extern_database, load_constants_database, load_constants_raw_database
from lgd_tool.lgd_decompiler.LGC_refiner.extern_refiner import refine_externs
from lgd_tool.lgd_decompiler.LGC_refiner.const_refiner import refine_constants

CONST_BLOCK_START = "// ===== AUTO GENERATED CONSTANTS START ====="
CONST_BLOCK_END = "// ===== AUTO GENERATED CONSTANTS END ====="


class LgcRefiner:
    """
    LGC 后处理优化器。
    从指定目录加载 extern 和 constants 数据库，
    对已生成的 LGC 文本执行符号替换。
    """

    def __init__(self, data_dir: Path):
        """
        :param data_dir: 数据目录路径（包含 extern_database.json 和 constants_database.json）
        """
        extern_path = data_dir / "extern_database.json"
        const_path = data_dir / "constants_database.json"

        self.extern_db = load_extern_database(extern_path)
        self.const_db = load_constants_database(const_path)
        self.const_raw_db = load_constants_raw_database(const_path)

    def refine(self, lgc_text: str, file_name: str = "") -> str:
        """
        对 LGC 文本执行精炼与优化。

        根据传入的文件名进行差异化处理：
        1. 以 .bak.lgc 结尾的备份文件将跳过全部优化以防破坏备份。
        2. 重组后的核心导出文件 export.lgc (或未指定文件名时) 将在文件头部注入常量声明，并执行 extern 替换和常量符号替换。
        3. 其他普通 LGC 文件不注入常量声明，但会执行 extern 替换和常量符号替换。

        :param lgc_text: 原始 LGC 文本内容
        :param file_name: 正在处理的 LGC 文件名 (例如 export.lgc)
        :return: 优化/替换后的 LGC 文本内容
        """
        if file_name:
            log_name = file_name
        else:
            log_name = "unknown"
        logger.info(f"[Refiner] Starting LGC refinement for file: {log_name}...")

        # 1. 过滤判断是否为备份文件（以 .bak.lgc 结尾）
        # 统一转为小写后判断是否以 .bak.lgc 结尾
        file_name_lower = file_name.lower()
        if file_name_lower.endswith(".bak.lgc"):
            logger.info(f"[Refiner] File '{file_name}' is a backup file, skipping all refinements.")
            return lgc_text

        # 2. 判断是否需要注入常量声明到文件头部
        # 只对没有指定文件名（向后兼容），或者文件名为 export.lgc 的文件进行常数注入
        if not file_name or file_name_lower == "export.lgc":
            logger.info(f"[Refiner] Injecting constants at the top of file: {log_name}")
            lgc_text = inject_all_constants_to_top(lgc_text, self.const_raw_db)
        else:
            logger.info(f"[Refiner] Skipping constant injection for non-export file: {log_name}")

        # 3. 对非备份文件执行其余优化（即 extern 替换和常量符号替换）
        logger.info(f"[Refiner] Applying externs and constants substitutions for file: {log_name}")
        lgc_text = refine_externs(lgc_text, self.extern_db)
        lgc_text = refine_constants(lgc_text, self.const_db)

        logger.info(f"[Refiner] LGC refinement completed for file: {log_name}")
        return lgc_text



def inject_all_constants_to_top(lgc_text: str, const_raw_db: dict) -> str:
    if not const_raw_db:
        return lgc_text

    const_block = _build_constants_block(const_raw_db)
    if not const_block:
        return lgc_text

    cleaned_text = _remove_previous_generated_block(lgc_text)
    insert_pos = _find_constants_insert_position(cleaned_text)
    if insert_pos is None:
        return const_block + "\n" + cleaned_text

    prefix = cleaned_text[:insert_pos]
    suffix = cleaned_text[insert_pos:]
    if prefix and not prefix.endswith("\n"):
        prefix = prefix + "\n"

    return prefix + const_block + "\n" + suffix


def _find_constants_insert_position(lgc_text: str):
    extern_header_pattern = re.compile(r'^\s*//\s*---\s*Extern\s+Definitions\s*---\s*$', re.MULTILINE | re.IGNORECASE)
    extern_header_match = extern_header_pattern.search(lgc_text)
    if extern_header_match is not None:
        header_start = extern_header_match.start()
        prev_line_start = lgc_text.rfind("\n", 0, header_start)
        if prev_line_start != -1:
            line_begin = lgc_text.rfind("\n", 0, prev_line_start)
            if line_begin == -1:
                line_begin = 0
            else:
                line_begin = line_begin + 1
            prev_line = lgc_text[line_begin:prev_line_start].strip()
            if prev_line.startswith("//") and "=" in prev_line:
                return line_begin
        return header_start

    extern_pattern = re.compile(r'^\s*extern\b', re.MULTILINE)
    extern_match = extern_pattern.search(lgc_text)
    if extern_match is not None:
        return extern_match.start()

    return None


def _remove_previous_generated_block(lgc_text: str) -> str:
    pattern = re.compile(
        re.escape(CONST_BLOCK_START) + r'.*?' + re.escape(CONST_BLOCK_END) + r'\n?',
        re.DOTALL
    )
    return pattern.sub("", lgc_text)


def _build_constants_block(const_raw_db: dict) -> str:
    lines = []
    lines.append("")
    lines.append(CONST_BLOCK_START)
    lines.append("// =======================================================")
    lines.append("// Auto generated from constants_database.json")
    lines.append("// Duplicate macro names are commented out to prevent compile errors")
    lines.append("// Conflicting values keep version tags in trailing comments")
    lines.append("// =======================================================")
    lines.append("")

    total_written = 0
    conflict_macros = 0
    conflict_entries = 0
    duplicate_comment_count = 0
    emitted_macro_names = {}

    for group, macros in const_raw_db.items():
        lines.append(f"// {'=' * 40}")
        lines.append(f"// Group: {group}")
        lines.append(f"// {'=' * 40}")

        for name, data in macros.items():
            values_dict = data.get("values", {})
            if not values_dict:
                continue

            if len(values_dict) > 1:
                conflict_macros += 1
                for val, versions in values_dict.items():
                    versions_str = ", ".join(versions)
                    is_duplicate = name in emitted_macro_names
                    if is_duplicate:
                        original_val = emitted_macro_names[name]
                        lines.append(
                            f"// #define {name} {val} // Versions: {versions_str} | "
                            f"Disabled duplicate, first value: {original_val}"
                        )
                        duplicate_comment_count += 1
                    else:
                        lines.append(f"#define {name} {val} // Versions: {versions_str}")
                        emitted_macro_names[name] = val
                    total_written += 1
                    conflict_entries += 1
            else:
                for val in values_dict.keys():
                    is_duplicate = name in emitted_macro_names
                    if is_duplicate:
                        original_val = emitted_macro_names[name]
                        lines.append(f"// #define {name} {val} // Disabled duplicate, first value: {original_val}")
                        duplicate_comment_count += 1
                    else:
                        lines.append(f"#define {name} {val}")
                        emitted_macro_names[name] = val
                    total_written += 1
        lines.append("")

    lines.append(CONST_BLOCK_END)
    logger.info(
        f"[Refiner] Constants header injected: total={total_written}, "
        f"conflict_macros={conflict_macros}, conflict_entries={conflict_entries}, "
        f"commented_duplicates={duplicate_comment_count}"
    )
    logger.warning(f"[Refiner] {conflict_entries} Duplicated Constants have been commented out ")
    return "\n".join(lines)
