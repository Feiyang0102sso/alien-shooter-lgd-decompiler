"""
/refine_data_prepare/generate_lgc_from_json.py
用于将提取并聚类的 JSON 常量数据库重新生成为 LGC 文件格式。
按组分类写入，遇到多版本冲突（同名不同值）的常量时，将输出警告，
并在生成的代码后追加注释标明其对应的版本名。
"""

import json
from pathlib import Path
from lgd_tool.logger import logger

# --- 环境初始化 ---
CURRENT_DIR = Path(__file__).resolve().parent

# --- 配置区 ---
JSON_CONSTANTS_PATH = CURRENT_DIR / "constants_database.json"
OUTPUT_LGC_FILE = CURRENT_DIR / "output" / "generated_constants.lgc"


def generate_lgc_from_json(json_path: Path, output_path: Path):
    if not json_path.exists():
        logger.error_and_stop(f"找不到指定的 JSON 数据库文件: {json_path}")
        return

    logger.info(f"开始加载 JSON 数据库: {json_path.name}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            db_data = json.load(f)
    except Exception as e:
        logger.error_and_stop(f"读取 JSON 数据库失败: {e}")
        return

    # 确保输出目录存在
    output_path.parent.mkdir(parents=True, exist_ok=True)

    stats = {"total_written": 0, "conflict_macros": 0, "conflict_entries": 0}

    logger.info(f"开始生成 LGC 文件: {output_path.name}")

    try:
        # 这里默认使用 utf-8 写入。如果你的 LGC 引擎严格要求 windows-1251，请修改 encoding 参数
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("// ========================================================\n")
            f.write("// 本文件由 JSON 常量数据库自动生成\n")
            f.write("// 多版本冲突的常量会在行尾标注其归属的版本\n")
            f.write("// ========================================================\n\n")

            # 遍历所有的组 (例如 "GENERAL", "VID" 等)
            for group, macros in db_data.items():
                # 写入组的分割注释
                f.write(f"// {'=' * 40}\n")
                f.write(f"// Group: {group}\n")
                f.write(f"// {'=' * 40}\n")

                for name, data in macros.items():
                    values_dict = data.get("values", {})

                    if not values_dict:
                        continue

                    # 检查是否存在同名但值不同的冲突
                    if len(values_dict) > 1:
                        stats["conflict_macros"] += 1
                        logger.warning(f"发现多值冲突: [{group}] {name} 存在 {len(values_dict)} 个不同的值分支！")

                        # 遍历该宏的所有不同值，追加带版本标注的注释
                        for val, versions in values_dict.items():
                            versions_str = ", ".join(versions)
                            f.write(f"#define {name} {val} // Versions: {versions_str}\n")
                            stats["total_written"] += 1
                            stats["conflict_entries"] += 1
                    else:
                        # 正常情况：只有一个值，直接生成纯净的宏定义
                        for val in values_dict.keys():
                            f.write(f"#define {name} {val}\n")
                            stats["total_written"] += 1

                # 每个组结束加一个空行
                f.write("\n")

    except Exception as e:
        logger.error_and_stop(f"写入 LGC 文件失败: {e}")

    logger.info("=" * 40)
    logger.info(f"LGC 生成完成！")
    logger.info(f" - 总计写入常量条目: {stats['total_written']} 个")
    logger.info(f" - 涉及冲突的宏数量: {stats['conflict_macros']} 个")
    logger.info(f" - 展开的冲突值条目: {stats['conflict_entries']} 个")
    logger.info("=" * 40)


if __name__ == "__main__":
    generate_lgc_from_json(JSON_CONSTANTS_PATH, OUTPUT_LGC_FILE)