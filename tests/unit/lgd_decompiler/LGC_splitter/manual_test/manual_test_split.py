"""
manual_test_split.py

用于手动测试 LGC 拆分器（LGC_splitter）切分功能的脚本。
该脚本读取真实的回归测试大文件 `regression_tutorial_00.lgc`，
在同级目录下创建一个临时的输出目录，并按照切分结果输出为子 lgc 文件。
用户可以直观地到该临时目录下查看各文件生产出来的函数和行号范围。
运行完毕后，按 Enter 键可以自动清空产生的所有临时文件。
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

from lgd_tool.lgd_decompiler.LGC_splitter import (
    parse_lgc_functions,
    decide_segments,
    write_segment_files,
)


def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取实际的反编译文件，进行切分判定，并将提取的各个段落写出为临时 lgc 文件供审查。
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

    # 2. 调用核心分割模块
    print("步骤 1: 正在从大 LGC 文件中提取顶层函数与行号注释...")
    functions = parse_lgc_functions(content)
    print(f"-> 成功解析出 {len(functions)} 个顶级函数。\n")

    print("步骤 2: 正在运行基于 `next.min_line < prev.max_line` 的回跳状态机切段...")
    segments = decide_segments(functions)

    export_list = segments["export"]
    segment_lists = segments["segments"]

    print(f"-> 划分结果:")
    print(f"   * 公共段 (export): {len(export_list)} 个函数")
    print(f"   * 普通段 (segments): {len(segment_lists)} 个段落")
    
    total_in_segments = 0
    for idx, seg in enumerate(segment_lists):
        total_in_segments += len(seg)
        # 获取该段首尾函数的行号变化，以便打印
        first_func = seg[0]
        last_func = seg[-1]
        print(
            f"     - 段 {idx + 1:02d}: 包含 {len(seg):2d} 个函数 "
            f"(范围: {first_func.min_line}~{first_func.max_line} 到 {last_func.min_line}~{last_func.max_line})"
        )
    print(f"   * 普通段累计覆盖函数: {total_in_segments} 个")
    print("-" * 70)

    # 3. 产生临时文件夹并输出段落内容以供直观验证
    temp_output_dir = _CURRENT_DIR / "_manual_test_temp"
    
    # 若先前残留了则先清空
    if temp_output_dir.exists():
        shutil.rmtree(temp_output_dir)
        
    print(f"步骤 3: 正在使用 write_segment_files 核心接口输出子 LGC 文件。临时输出目录:\n   {temp_output_dir}\n")
    write_segment_files(segments, temp_output_dir, lgc_file_path.name)

    print("\n" + "=" * 70)
    print("手动测试生成就绪！")
    print("您可以立即到资源管理器或编辑器中打开 `_manual_test_temp` 目录审查各子文件。")
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
