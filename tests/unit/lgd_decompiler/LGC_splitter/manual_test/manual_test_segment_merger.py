"""
manual_test_segment_merger.py

针对 LGC 拆分器中普通代码段（Segment）哈希去重比对、差一字节拦截以及动态文件名序列绑定的手动测试脚本。
该脚本完全在内存中手写构造 3 个关卡的普通代码段数据：
  - 关卡 1 (level_01.lgc): 包含一个普通代码段（内含 funcA）
  - 关卡 2 (level_02.lgc): 包含两个普通代码段：
      1. 第 1 段内容与关卡 1 的段完完全全 100% 一致 (内含 funcA)
      2. 第 2 段内容为一个全新的不同普通段 (内含 funcB)
  - 关卡 3 (level_03.lgc): 包含一个普通代码段，内容与 funcA 高度相似，但尾部故意多出一个空格（仅差一字节空格！）

直观向用户演示并审查：
  1. 内容完全一致的普通段 100% 被成功合并去重，物理磁盘仅写出一份 segment_01.lgc。
  2. 新普通段成功写出为 segment_02.lgc。
  3. 尾部仅相差一个空格的段被严苛判定为不同段，绝对不发生强行合并，物理上写出为 segment_03.lgc（落实了“差一个字节都不行”）。
  4. 审查各大文件被成功还原生成的有序引用链序列。
  5. 最终提供一键 Enter 清扫临时残留垃圾。
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

from lgd_tool.lgd_decompiler.LGC_reorganizer import (
    LgcFunction,
    LgcSegmentPool,
)


def run_manual_test() -> None:
    """
    手动测试核心逻辑函数。
    """
    print("=" * 80)
    print("【手动测试】LGC 多文件普通代码段 (Segment) 哈希去重与引用绑定工具")
    print("=" * 80)

    # 1. 模拟构造段 1 (funcA)
    func_a = LgcFunction(
        name="funcA",
        start_line_idx=10,
        lines=[
            "funcA()",
            "{",
            "    int x = 1;",
            "}"
        ]
    )
    seg_a = [func_a]

    # 2. 模拟构造段 2 (与 funcA 完完全全 100% 相同)
    func_a_identical = LgcFunction(
        name="funcA",
        start_line_idx=20,
        lines=[
            "funcA()",
            "{",
            "    int x = 1;",
            "}"
        ]
    )
    seg_a_identical = [func_a_identical]

    # 3. 模拟构造段 3 (全新段，内容为 funcB)
    func_b = LgcFunction(
        name="funcB",
        start_line_idx=30,
        lines=[
            "funcB()",
            "{",
            "    string name = \"Addon0\";",
            "}"
        ]
    )
    seg_b = [func_b]

    # 4. 模拟构造段 4 (与 funcA 极为相似，但尾部故意多出了一个空格！仅一字节之差！)
    func_a_with_space = LgcFunction(
        name="funcA",
        start_line_idx=40,
        lines=[
            "funcA()",
            "{",
            "    int x = 1; ", # 注意等号后面有空格
            "}"
        ]
    )
    seg_a_bad_space = [func_a_with_space]

    # 5. 创建物理输出的临时目录
    temp_dir = _CURRENT_DIR / "_manual_segments_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # 6. 初始化全局哈希段池
    pool = LgcSegmentPool(temp_dir)

    print("步骤 1: 正在调用 register_file_segments 核心算法注册三大文件...")
    print("        [提示] 正在执行“差一个字节都不行”的内容指纹 MD5 精确比对...\n")

    # 注册关卡 1 的段 (只有 1 个段)
    pool.register_file_segments("level_01.lgc", [seg_a])
    
    # 注册关卡 2 的段 (共有 2 个段: 第 1 段是 funcA 去重合并，第 2 段是 funcB 新段)
    pool.register_file_segments("level_02.lgc", [seg_a_identical, seg_b])
    
    # 注册关卡 3 的段 (只有 1 个段: 多了一个空格，应当判定为新段)
    pool.register_file_segments("level_03.lgc", [seg_a_bad_space])

    # 7. 对生成的文件内容与大文件的引用序列进行直观展示
    print("\n" + "=" * 80)
    print("【直观成果审查 - 差一个字节都不行】")
    print("=" * 80)

    # 7.1 审查磁盘写出文件
    print(f"\n>>> 1. 物理磁盘成功写出的去重文件列表: {temp_dir.relative_to(_PROJECT_ROOT)}")
    print("-" * 60)
    written_files = sorted(list(temp_dir.glob("*.lgc")))
    for f in written_files:
        print(f"  * {f.name} (大小: {f.stat().st_size} 字节)")
    print("-" * 60)

    # 7.2 审查各大文件被成功解析和解耦的有序引用链序列
    print("\n>>> 2. 各大文件在编译载入时的 [有序引用关系链] 对比 (解耦引用物理位置):")
    print("-" * 60)
    for name, refs in pool.file_references.items():
        print(f"  * 文件 '{name}' 共有 {len(refs)} 个代码段依赖:")
        for idx, ref in enumerate(refs):
            print(f"    - 段 [{idx + 1:02d}] -> 指向物理文件: {ref}")
    print("-" * 60)

    # 7.3 精确比对 segment_01.lgc 与 segment_03.lgc 尾部的字节差异，证实严苛性
    print("\n>>> 3. 精确字节级细节比对 (证实“差一个字节都不行”):")
    print("-" * 60)
    lines_01 = (temp_dir / "segment_01.lgc").read_text(encoding="utf-8").splitlines()
    lines_03 = (temp_dir / "segment_03.lgc").read_text(encoding="utf-8").splitlines()
    # 比较 funcA 体内的第 7 行
    print(f"  * 'segment_01.lgc' (第 7 行): {repr(lines_01[6])}")
    print(f"  * 'segment_03.lgc' (第 7 行): {repr(lines_03[6])}")
    print("  * 判定: 虽然逻辑相同，但因多出一个排版空格，字节指纹不同，绝对不发生强行合并！")
    print("-" * 60)

    print("\n" + "=" * 80)
    print("手动测试演示完毕！")
    print(f"物理临时目录在: {temp_dir.relative_to(_PROJECT_ROOT)}")
    print("=" * 80)

    # 8. 等待回车，清扫垃圾维持完美零残留
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
