"""
/refine_data_prepare/prepare_constants_data.py
用于从官方泄露的 LGC 源码中提取 #define 常量。
利用命名约定的前缀（如 VID_, ACT_, COM_）进行自动聚类，忽略不可靠的注释。
支持记录同名但在不同版本下拥有不同值的常量宏。
"""

import json
import re
from pathlib import Path
from logger import logger

# --- 环境初始化 ---
CURRENT_DIR = Path(__file__).resolve().parent

# --- 配置区 ---
# TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_ASLC_Android_1.1.4.lgc"
# TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_ASTB.lgc"
TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_AS2TL_Beta.lgc"
JSON_CONSTANTS_PATH = CURRENT_DIR / "output" /"constants_database.json"

# 正则解析 #define
# 匹配: #define NAME VALUE //可选注释
# 注意：排除了带括号的宏函数，比如 #define GETSPRITE_TYPE(t)
DEFINE_PATTERN = re.compile(
    r'^\s*#define\s+(?P<name>[a-zA-Z_][a-zA-Z0-9_]*)\s+(?P<value>.*?)(?://.*|/\*.*)?$'
)


def extract_version_from_filename(filename: str) -> str:
    match = re.match(r'^export_(.+?)\.lgc$', filename, re.IGNORECASE)
    return match.group(1) if match else "unknown_version"


def process_constants(lgc_file_path: Path, db_path: Path):
    if not lgc_file_path.exists():
        logger.error_and_stop(f"找不到指定的 LGC 文件: {lgc_file_path}")
        return

    version = extract_version_from_filename(lgc_file_path.name)
    logger.info(f"开始提取常量: {lgc_file_path.name} | 版本: {version}")

    # 新版 db_data 结构:
    # { "GROUP": { "MACRO": {"values": {"val1": ["v1", "v2"], "val2": ["v3"]}} } }
    db_data = {}
    if db_path.exists():
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            logger.info(f"成功加载现有常量数据库，当前组数: {len(db_data)}")
        except Exception as e:
            logger.error_and_stop(f"读取现有 JSON 数据库失败: {e}")

    stats = {"total_found": 0, "new_added": 0, "merged_version": 0, "value_conflict": 0}
    newly_added_items = []

    with open(lgc_file_path, 'r', encoding='windows-1251') as f:
        for line_num, line in enumerate(f, 1):
            match = DEFINE_PATTERN.search(line)
            if not match:
                continue

            name = match.group('name').strip()
            value = match.group('value').strip()

            # 过滤掉空值或纯粹为了防卫的宏，如 #ifndef EXPORT_H 下的 #define EXPORT_H aaa
            if not value or name in ["EXPORT_H"]:
                continue

            stats["total_found"] += 1

            # 核心聚类逻辑：以第一个 '_' 前的单词作为组名
            if '_' in name:
                group = name.split('_')[0].upper()
            else:
                group = "GENERAL"  # 没下划线的（如 true, false）放进通用组

            if group not in db_data:
                db_data[group] = {}

            if name in db_data[group]:
                # 兼容升级旧的数据库结构：将旧的 {"value": x, "versions": []} 转为新的 {"values": {x: []}}
                if "value" in db_data[group][name]:
                    old_v = db_data[group][name].pop("value")
                    old_vers = db_data[group][name].pop("versions", [])
                    db_data[group][name]["values"] = {old_v: old_vers}

                # 开始检查多值逻辑
                if value not in db_data[group][name]["values"]:
                    # 发现多版本常量冲突！
                    # 收集该常量所有的历史值和关联版本，以便在 Warning 中详尽输出
                    history_details = []
                    for h_val, h_vers in db_data[group][name]["values"].items():
                        history_details.append(f"{h_val} (历史版本: {', '.join(h_vers)})")
                    history_str = " | ".join(history_details)

                    # 抛出非常详细的警告日志
                    logger.warning(
                        f"常量值冲突! {name} 的历史记录为 [{history_str}], "
                        f"但在当前新版本 [{version}] 中变成了 [{value}]. 已为您保留所有多版本条目。"
                    )

                    # 记录这个新的数值分支
                    db_data[group][name]["values"][value] = [version]
                    stats["value_conflict"] += 1
                    newly_added_items.append(f"[{group}] {name} = {value} (触发多版本冲突保留)")
                else:
                    # 数值相同，仅需合并版本
                    if version not in db_data[group][name]["values"][value]:
                        db_data[group][name]["values"][value].append(version)
                        stats["merged_version"] += 1
            else:
                # 第一次遇到的新宏，按照嵌套 values 结构初始化
                db_data[group][name] = {
                    "values": {
                        value: [version]
                    }
                }
                stats["new_added"] += 1
                newly_added_items.append(f"[{group}] {name} = {value}")

    # 保存
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error_and_stop(f"保存 JSON 常量数据库失败: {e}")

    logger.info("=" * 40)
    logger.info(f"常量提取完成！")
    logger.info(f" - 总计发现: {stats['total_found']} 个常量")
    logger.info(f" - 新增常量: {stats['new_added']} 个")
    logger.info(f" - 版本合并: {stats['merged_version']} 个")
    logger.info(f" - 多值冲突: {stats['value_conflict']} 个 (已全部独立保留)")
    logger.info(f" - 当前总组数: {len(db_data)}")
    logger.info("=" * 40)

    if newly_added_items:
        logger.debug("--- 本次新增的常量列表 ---")
        for item in newly_added_items:
            logger.debug(item)
        logger.debug("-" * 28)


if __name__ == "__main__":
    process_constants(TARGET_LGC_FILE, JSON_CONSTANTS_PATH)