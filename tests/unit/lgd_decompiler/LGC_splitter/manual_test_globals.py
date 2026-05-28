"""
manual_test_globals.py

用于手动测试 LGC 拆分器中全局变量（Global Var）提取与保存功能的脚本。
该脚本读取真实的回归测试大文件 `regression_tutorial_00.lgc`，
在同级目录下创建一个临时的输出目录，将提取出的所有全局变量声明输出到 `global_variable.lgc` 中。
用户可以直观地到该临时目录下查看生成的全局变量。
运行完毕后，按 Enter 键会自动清空产生的所有临时文件。
"""

import sys
import shutil
from pathlib import Path

# 将项目根目录与 src 目录加入 Python 寻路路径，以便能正常导入我们的核心库
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[3]
_SRC_DIR = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import (
    extract_globals_from_content,
    write_global_variable_file,
)


def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取实际的 LGC 反编译文件，提取所有的全局变量声明，并写出到临时全局变量文件中供审查。
    """
    # 真实测试用例物理路径
    lgc_file_path = (
        _PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "regression_lgc"
        / "regression_tutorial_00.lgc"
    )

    if not lgc_file_path.exists():
        print(f"[错误] 未找到真实的测试文件: {lgc_file_path}")
        return

    print("=" * 70)
    print(f"正在读取真实 LGC 文件: {lgc_file_path.name} ({lgc_file_path.stat().st_size / 1024:.1f} KB)")
    print("=" * 70)

    # 1. 读取大文件内容
    content = lgc_file_path.read_text(encoding="utf-8", errors="replace")

    # 2. 调用全局变量提取模块
    print("步骤 1: 正在从大 LGC 文件中匹配并提取全局变量声明...")
    globals_list = extract_globals_from_content(content)
    total_count = len(globals_list)
    print(f"-> 成功提取出 {total_count} 个全局变量声明。\n")

    # 打印前 5 个和后 5 个全局变量
    print("-" * 70)
    print("前 5 个提取的全局变量示例:")
    for idx in range(min(5, total_count)):
        print(f"  [{idx:03d}] {globals_list[idx]}")
    print("\n后 5 个提取的全局变量示例:")
    for idx in range(max(0, total_count - 5), total_count):
        print(f"  [{idx:03d}] {globals_list[idx]}")
    print("-" * 70)

    # 3. 产生临时文件夹并输出以供直观验证
    temp_output_dir = _CURRENT_DIR / "_manual_globals_temp"

    # 若先前残留了则先清空
    if temp_output_dir.exists():
        shutil.rmtree(temp_output_dir)

    temp_output_dir.mkdir(parents=True, exist_ok=True)
    print(f"步骤 2: 正在生成临时的 global_variable.lgc。临时输出目录:\n   {temp_output_dir}\n")

    output_file = temp_output_dir / "global_variable.lgc"
    write_global_variable_file(globals_list, output_file)

    if output_file.exists():
        print(f"  [已生成] {output_file.name} (大小: {output_file.stat().st_size} 字节)")

    print("\n" + "=" * 70)
    print("手动测试生成就绪！")
    print("您可以立即到资源管理器或编辑器中打开 `_manual_globals_temp` 目录审查导出的 `global_variable.lgc` 文件。")
    print("=" * 70)

    # 4. 等待用户确认，然后自动清除所有临时生成的文件
    try:
        input("\n>>> 【审查完毕后，请按 Enter 键清空这些临时产生的文件并退出】 <<< ")
    except KeyboardInterrupt:
        pass

    print("\n正在清理临时目录...")
    if temp_output_dir.exists():
        shutil.rmtree(temp_output_dir)
        print("-> 临时目录已彻底清理干净。")

    print("测试完毕。")


if __name__ == "__main__":
    run_manual_test()
