"""
LGC_refiner/database_loader.py
负责从 data/decompiler_refiner 目录加载 extern 和 constants 两个 JSON 数据库。
"""

import json
from pathlib import Path
from lgd_tool.logger import logger


def load_extern_database(json_path: Path) -> dict:
    """
    加载 extern_database.json 并构建查找索引。

    返回: {extern_id: [ExternEntry, ...]}
    每个 ExternEntry 是原始 JSON 中的一个条目字典，包含 name, id, params, official_decl 等。
    同一个 id 可能有多个条目（不同参数数量的重载）。
    """
    logger.debug(f"[Refiner] Loading extern database: {json_path}")

    if not json_path.exists():
        logger.warning(f"[Refiner] Extern database not found: {json_path}")
        return {}

    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 构建 {id: [entry, ...]} 索引
    db = {}
    for key, entry in raw_data.items():
        ext_id = entry["id"]
        if ext_id not in db:
            db[ext_id] = []
        db[ext_id].append(entry)

    logger.debug(f"[Refiner] Extern database loaded: {len(raw_data)} entries, {len(db)} unique IDs")
    return db


def load_constants_database(json_path: Path) -> dict:
    """
    加载 constants_database.json 并构建反向查找索引。

    返回: {prefix_group: {int_value: const_name}}
    例如: {"ACT": {5: "ACT_DESTROY_UNIT", 10: "ACT_ADD_AMMO"}, ...}

    值统一转为 int 以便匹配时不依赖字符串格式。
    """
    logger.debug(f"[Refiner] Loading constants database: {json_path}")

    if not json_path.exists():
        logger.warning(f"[Refiner] Constants database not found: {json_path}")
        return {}

    with open(json_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    # 构建 {prefix_group: {int_value: const_name}} 反向索引
    db = {}
    for group_name, constants in raw_data.items():
        value_map = {}
        for const_name, const_info in constants.items():
            values_dict = const_info.get("values", {})
            for val_str in values_dict.keys():
                int_val = _parse_value_to_int(val_str)
                if int_val is not None:
                    value_map[int_val] = const_name
        db[group_name] = value_map

    logger.debug(f"[Refiner] Constants database loaded: {len(db)} prefix groups")
    return db


def _parse_value_to_int(val_str: str):
    """
    将常量数据库中的值字符串转为 int。
    支持: "123", "-1", "0x1B", "0xFF00"
    对于非数值的字符串（如 '"male"', 'int'），返回 None。
    """
    val_str = val_str.strip()

    # 跳过带引号的字符串值和类型名
    if val_str.startswith('"') or val_str in ('int', 'string', 'bool'):
        return None

    if val_str.startswith("0x") or val_str.startswith("0X"):
        return int(val_str, 16)

    # 十进制（含负数）
    if val_str.lstrip('-').isdigit():
        return int(val_str)

    return None
