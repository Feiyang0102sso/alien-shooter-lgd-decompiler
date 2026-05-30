"""
tests/unit/lgd_decompiler/LGC_refiner/test_refiner_diff.py
测试 LgcRefiner 面对不同类型文件 (.bak.lgc, export.lgc, segment_xx.lgc) 时的精炼差异化规则。
"""

import json
from pathlib import Path
from lgd_tool.lgd_decompiler.LGC_refiner.refiner import LgcRefiner


def test_lgc_refiner_differentiation(tmp_path: Path):
    """
    测试 LgcRefiner 针对备份文件、主入口文件和普通分段文件的差异化精炼优化策略。
    """
    # 1. 创建临时的外部符号与常量数据库
    extern_db_path = tmp_path / "extern_database.json"
    const_db_path = tmp_path / "constants_database.json"

    # 外部函数数据库模拟（遵循 database_loader 与 extern_refiner 的结构要求）
    extern_data = {
        "OldFunc": {
            "id": 999,
            "name": "OldFunc",
            "official_decl": "extern NewFunc() 999;",
            "params": []
        }
    }
    extern_db_path.write_text(json.dumps(extern_data), encoding="utf-8")

    # 常量数据库模拟，包含 ENV 组及 MY_CONST 常量
    const_data = {
        "ENV": {
            "MY_CONST": {
                "values": {
                    "100": ["v1"]
                }
            }
        }
    }
    const_db_path.write_text(json.dumps(const_data), encoding="utf-8")

    # 2. 实例化 LgcRefiner
    refiner = LgcRefiner(tmp_path)

    # 3. 准备待测试的 LGC 原始文本
    # 注意：常量宏的替换只在特定函数的指定参数位置生效，这里使用 SetEnvironment(100);
    raw_lgc = (
        "// test code\n"
        "extern OldFunc() 999;\n"
        "SetEnvironment(100);\n"
    )

    # 4. 测试案例 A：备份文件 (xxx.bak.lgc) 应直接跳过所有优化
    refined_bak = refiner.refine(raw_lgc, file_name="level_07.bak.lgc")
    # 应与原始文本完全一致
    assert refined_bak == raw_lgc

    # 5. 测试案例 B：导出核心文件 (export.lgc) 应进行常数注入 + 符号替换
    refined_export = refiner.refine(raw_lgc, file_name="export.lgc")
    # 应该包含常数宏注入块
    assert "// ===== AUTO GENERATED CONSTANTS START =====" in refined_export
    assert "#define MY_CONST 100" in refined_export
    # 应该进行了 extern 和 constants 替换
    assert "extern NewFunc() 999;" in refined_export
    assert "SetEnvironment(MY_CONST);" in refined_export

    # 6. 测试案例 C：普通分段文件 (segment_01.lgc) 应只进行符号替换，不注入常数宏定义
    refined_segment = refiner.refine(raw_lgc, file_name="segment_01.lgc")
    # 不应该包含常数宏注入块
    assert "// ===== AUTO GENERATED CONSTANTS START =====" not in refined_segment
    # 应该进行了 extern 和 constants 替换
    assert "extern NewFunc() 999;" in refined_segment
    assert "SetEnvironment(MY_CONST);" in refined_segment

    # 7. 测试案例 D：不传文件名（向后兼容）应保留默认行为（常数注入 + 符号替换）
    refined_default = refiner.refine(raw_lgc)
    assert "// ===== AUTO GENERATED CONSTANTS START =====" in refined_default
    assert "extern NewFunc() 999;" in refined_default
    assert "SetEnvironment(MY_CONST);" in refined_default
