"""
manual_test_global_var_merger.py

针对 LGC 拆分器中全局变量（Global Variables）合并、差异化分流与主入口脚本头部注入的手动测试脚本。
该脚本完全在内存中手写构造 3 个模拟文件的数据：
  - 模拟文件 1 (level_01.lgc): 包含公共变量 int SoundVolume; 和变量 int StartTeleport = 0;
  - 模拟文件 2 (level_02.lgc): 全局变量与文件 1 完全相同 (int SoundVolume; 和 int StartTeleport = 0;)
  - 模拟文件 3 (level_03.lgc): 包含公共变量 int SoundVolume; 和同名但赋值不同的变量 int StartTeleport = 1;

直观向用户演示并审查：
  1. 公共变量 int SoundVolume; 被成功合并提取并写入 core/global_variable.lgc。
  2. 冲突变量 StartTeleport 触发了 logger.warning 警示。
  3. 冲突变量按定义分别精准注入到了各自对应文件（level_01、level_02 与 level_03）的主入口脚本最开头。
  4. 最终提供一键 Enter 清扫临时残留垃圾。
"""

import sys
import shutil
from pathlib import Path

# 将项目根目录与 src 目录加入 Python 寻路路径
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[3]
_SRC_DIR = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from lgd_tool.lgd_decompiler.LGC_splitter import process_global_variables


def run_manual_test() -> None:
    """
    手动测试核心逻辑函数。
    手动构造模拟数据，调用核心比对注入接口，落盘写出并展示内容。
    """
    print("=" * 80)
    print("【手动测试】LGC 多文件 Global-Var 合并分流与主脚本注入比对工具")
    print("=" * 80)

    # 1. 手动构造 3 个文件的全局变量数据
    # 其中 1 和 2 基本一致，3 包含一个同名但赋值不同的冲突变量
    # 特别测试：int a = 0; 虽说只在 level_01.lgc 中声明，但因没有任何冲突，也应顺利并入公共全局变量！
    file_to_globals = {
        "level_01.lgc": [
            "int SoundVolume;",
            "int StartTeleport = 0;", # 变量名 StartTeleport，赋值为 0
            "int a = 0;"              # 仅在 level_01 中出现但无冲突，应并入公共全局变量
        ],
        "level_02.lgc": [
            "int SoundVolume;",
            "int StartTeleport = 0;" # 变量名 StartTeleport，赋值为 0 (与 1 完全相同)
        ],
        "level_03.lgc": [
            "int SoundVolume;",
            "int StartTeleport = 1;" # 变量名 StartTeleport，赋值为 1 (与 1, 2 冲突!)
        ]
    }


    # 2. 手动构造 3 个主入口脚本（最后一个段）的原始行代码
    file_last_segment_lines = {
        "level_01.lgc": [
            "#include \"core\\export.lgc\"",
            "#include \"core\\global_variable.lgc\"",
            "func_level_01_main()",
            "{",
            "    // --- Line 100 ---",
            "    StartTeleport = 0;",
            "}"
        ],
        "level_02.lgc": [
            "#include \"core\\export.lgc\"",
            "#include \"core\\global_variable.lgc\"",
            "func_level_02_main()",
            "{",
            "    // --- Line 200 ---",
            "    StartTeleport = 0;",
            "}"
        ],
        "level_03.lgc": [
            "#include \"core\\export.lgc\"",
            "#include \"core\\global_variable.lgc\"",
            "func_level_03_main()",
            "{",
            "    // --- Line 300 ---",
            "    StartTeleport = 1;",
            "}"
        ]
    }

    # 3. 创建物理输出的临时目录
    temp_dir = _CURRENT_DIR / "_manual_globals_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    print("步骤 1: 正在调用 process_global_variables 核心合流算法...")
    print("        [提示] 遇到冲突变量 StartTeleport 时，控制台将输出黄色 WARNING 警报。\n")
    
    # 4. 执行合流比对与局部注入核心算法
    updated_segments = process_global_variables(
        file_to_globals=file_to_globals,
        file_last_segment_lines=file_last_segment_lines,
        output_dir=temp_dir
    )

    print("\n步骤 2: 正在将注入后的主入口段文件物理写盘...")
    # 5. 物理写出主入口脚本
    for file_name, lines in updated_segments.items():
        out_path = temp_dir / file_name
        # 按照 standard 格式写入
        file_content_lines = []
        file_content_lines.append("// ==========================================")
        file_content_lines.append(f"// Entrance Script Segment: {file_name}")
        file_content_lines.append("// ==========================================")
        file_content_lines.append("")
        for line in lines:
            file_content_lines.append(line)
        file_content_lines.append("")
        
        out_path.write_text("\n".join(file_content_lines), encoding="utf-8")
        print(f"  [已生成] {file_name} (物理大小: {out_path.stat().st_size} 字节)")

    # 6. 对生成的文件内容进行直观展示，供用户直观审查
    print("\n" + "=" * 80)
    print("【直观成果审查 - 差一个字节都不行】")
    print("=" * 80)

    # 6.1 审查公共全局变量
    public_file_path = temp_dir / "core" / "global_variable.lgc"
    if public_file_path.exists():
        print(f"\n>>> 1. 公共变量文件: {public_file_path.name}")
        print("-" * 50)
        print(public_file_path.read_text(encoding="utf-8").strip())
        print("-" * 50)

    # 6.2 审查 level_01.lgc 主入口注入后的最开头代码行
    level_01_path = temp_dir / "level_01.lgc"
    if level_01_path.exists():
        print(f"\n>>> 2. 模拟文件 1 ({level_01_path.name}) 头部注入实况:")
        print("-" * 50)
        # 只打印前 12 行方便直观查看
        lines = level_01_path.read_text(encoding="utf-8").splitlines()
        for idx in range(min(12, len(lines))):
            print(f"  [{idx + 1:02d}] {lines[idx]}")
        print("  ...")
        print("-" * 50)

    # 6.3 审查 level_03.lgc 主入口注入后的最开头代码行（应与 01 的赋值不同）
    level_03_path = temp_dir / "level_03.lgc"
    if level_03_path.exists():
        print(f"\n>>> 3. 模拟文件 3 ({level_03_path.name}) 头部注入实况:")
        print("-" * 50)
        lines = level_03_path.read_text(encoding="utf-8").splitlines()
        for idx in range(min(12, len(lines))):
            print(f"  [{idx + 1:02d}] {lines[idx]}")
        print("  ...")
        print("-" * 50)

    print("\n" + "=" * 80)
    print("手动测试演示完毕！")
    print(f"物理临时目录在: {temp_dir.relative_to(_PROJECT_ROOT)}")
    print("=" * 80)

    # 7. 等待回车，清扫垃圾维持完美零残留
    try:
        input("\n>>> 【审查完毕后，请按 Enter 键清空这些临时产生的文件并退出】 <<< ")
    except KeyboardInterrupt:
        pass

    print("\n正在清理临时目录...")
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        print("-> 临时目录已彻底清理干净。")
    print("测试完毕。")


if __name__ == "__main__":
    run_manual_test()
