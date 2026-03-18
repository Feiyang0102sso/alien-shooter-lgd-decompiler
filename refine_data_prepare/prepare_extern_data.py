"""
/refine_data_prepare/prepare_extern_data.py
用于从官方泄露的 LGC 源码中提取 extern 声明，并根据特征指纹构建/合并到 JSON 数据库中。
自动过滤注释，生成干净的 official_decl 供后续 Refiner 替换使用。
"""

import json
import re
from pathlib import Path
from logger import logger

# --- 环境初始化 ---
# 确保能够正确导入项目根目录的 config 和 logger
CURRENT_DIR = Path(__file__).resolve().parent

# --- 配置区 ---
# 当前处理的源文件路径
# TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_ASLC_Android_1.1.4.lgc"
# TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_AS2TL_Beta.lgc"
TARGET_LGC_FILE = CURRENT_DIR / "data" / "export_ASTB.lgc"

# JSON 数据库保存路径
JSON_DB_PATH = CURRENT_DIR / "output" / "extern_database.json"

# 解析 extern 的正则：匹配 "extern FunctionName(args) ID" 忽略分号和后续注释
# Group 1: 函数名 (name)
# Group 2: 参数列表 (args)
# Group 3: ID (id)
EXTERN_PATTERN = re.compile(r'^\s*extern\s+(?P<name>\w+)\s*\((?P<args>.*?)\)\s*(?P<id>\d+)')


def extract_version_from_filename(filename: str) -> str:
    """
    从文件名中提取版本标识。
    例如: "export_ASLC_Android_1.1.4.lgc" -> "ASLC_Android_1.1.4"
    """
    match = re.match(r'^export_(.+?)\.lgc$', filename, re.IGNORECASE)
    if match:
        return match.group(1)
    return "unknown_version"


def parse_parameters(args_str: str) -> list:
    """
    解析括号内的参数字符串，返回结构化参数列表。
    例如: "int command, string regKey = \"\", int var0 = 0"
    返回: [
        {"type": "int", "name": "command", "default": None},
        {"type": "string", "name": "regKey", "default": '""'},
        {"type": "int", "name": "var0", "default": "0"}
    ]
    """
    params = []
    args_str = args_str.strip()
    if not args_str:
        return params

    # 按照逗号分割参数 (由于游戏脚本默认值基本不含嵌套逗号，直接 split 是安全的)
    raw_params = args_str.split(',')

    for rp in raw_params:
        rp = rp.strip()

        # 拆分默认值
        if '=' in rp:
            decl_part, def_part = rp.split('=', 1)
            decl_part = decl_part.strip()
            def_val = def_part.strip()
        else:
            decl_part = rp
            def_val = None

        # 拆分类型和变量名 (使用 rsplit 以安全处理 "unsigned int varName" 这种带空格的类型)
        parts = decl_part.rsplit(None, 1)
        if len(parts) == 2:
            p_type, p_name = parts
        else:
            p_type = parts[0]
            p_name = "unknown"

        params.append({
            "type": p_type.strip(),
            "name": p_name.strip(),
            "default": def_val
        })

    return params


def generate_fingerprint_key(name: str, fn_id: str, params: list) -> str:
    """
    根据函数名、ID、参数类型和默认值生成唯一的结构化特征指纹 (Hash Key)。
    例如: RegCommand_212_int_string=""_int=0
    """
    key_parts = [f"{name}_{fn_id}"]

    for p in params:
        # 去除类型中的多余空格进行标准化 (例如 'STRING *' -> 'STRING*')
        t = p['type'].replace(" ", "")

        if p['default'] is not None:
            # 默认值如果是空字符串字面量 '""'，直接拼入
            d = p['default'].replace(" ", "") if '"' not in p['default'] else p['default']
            key_parts.append(f"{t}={d}")
        else:
            key_parts.append(t)

    return "_".join(key_parts)


def process_lgc_file(lgc_file_path: Path, db_path: Path):
    """
    核心业务逻辑：读取单个 LGC 文件，解析 extern，合并至 JSON 数据库。
    并在最后使用 logger 输出详尽的总结。
    """
    if not lgc_file_path.exists():
        logger.error_and_stop(f"找不到指定的 LGC 文件: {lgc_file_path}")
        return

    # 1. 提取版本号
    version = extract_version_from_filename(lgc_file_path.name)
    logger.info(f"开始解析源文件: {lgc_file_path.name} | 识别版本: {version}")

    # 2. 加载或初始化数据库
    db_data = {}
    if db_path.exists():
        try:
            with open(db_path, 'r', encoding='utf-8') as f:
                db_data = json.load(f)
            logger.info(f"成功加载现有数据库，当前条目数: {len(db_data)}")
        except Exception as e:
            logger.error_and_stop(f"读取现有 JSON 数据库失败: {e}")

    # 3. 统计计数器与新增列表
    stats = {
        "total_found": 0,
        "new_added": 0,
        "merged_version": 0,
        "duplicate_in_same_file": 0
    }
    newly_added_items = []  # 用于记录本次执行新增的声明

    # 4. 逐行读取与解析
    with open(lgc_file_path, 'r', encoding='windows-1251') as f:
        for line_num, line in enumerate(f, 1):
            match = EXTERN_PATTERN.search(line)
            if not match:
                continue

            stats["total_found"] += 1
            name = match.group('name')
            args_str = match.group('args')
            fn_id = match.group('id')

            # 重组纯净版声明 (去除后面的乱七八糟的注释，强行加上分号)
            clean_decl = f"extern {name}({args_str.strip()}) {fn_id};"

            # 解析参数提取特征
            params = parse_parameters(args_str)
            fingerprint = generate_fingerprint_key(name, fn_id, params)

            # 5. 数据库合并逻辑 (Upsert)
            if fingerprint in db_data:
                # 记录存在，检查版本
                if version not in db_data[fingerprint]["versions"]:
                    db_data[fingerprint]["versions"].append(version)
                    stats["merged_version"] += 1
                else:
                    stats["duplicate_in_same_file"] += 1
            else:
                # 新记录
                db_data[fingerprint] = {
                    "name": name,
                    "id": int(fn_id),
                    "versions": [version],
                    "official_decl": clean_decl,
                    "params": params
                }
                stats["new_added"] += 1
                newly_added_items.append(clean_decl)  # 记录纯净版声明

    # 6. 保存回写数据库
    db_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(db_path, 'w', encoding='utf-8') as f:
            json.dump(db_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        logger.error_and_stop(f"保存 JSON 数据库失败: {e}")

    # 7. 打印执行总结报告
    logger.info("=" * 40)
    logger.info(f"解析任务完成！总结报告如下：")
    logger.info(f" - 读取文件: {lgc_file_path.name}")
    logger.info(f" - 提取版本: {version}")
    logger.info(f" - 总计发现: {stats['total_found']} 个 extern 声明")
    logger.info(f" - 新增选项: {stats['new_added']} 个新函数指纹被收录")
    logger.info(f" - 版本合并: {stats['merged_version']} 个指纹与旧版本完全一致并追加了版本号")
    if stats["duplicate_in_same_file"] > 0:
        logger.warning(f" - 重复发现: 发现 {stats['duplicate_in_same_file']} 个在同一文件内的完全重复声明")
    logger.info(f" - 数据库现存总条目数: {len(db_data)}")
    logger.info(f" - 数据库文件路径: {db_path}")
    logger.info("=" * 40)

    # 8. 打印新增的条目详细内容 (DEBUG 级别)
    if newly_added_items:
        logger.debug("--- 本次执行新增的 extern 声明详细列表 ---")
        for item in newly_added_items:
            logger.debug(f"[新增] {item}")
        logger.debug("-" * 42)


if __name__ == "__main__":
    process_lgc_file(TARGET_LGC_FILE, JSON_DB_PATH)