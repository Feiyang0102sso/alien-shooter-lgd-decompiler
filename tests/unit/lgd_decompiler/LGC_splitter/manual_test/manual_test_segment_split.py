"""
manual_test_segment_split.py

"""

from manual_test_utils import load_tutorial_lgc_content, setup_temp_dir, wait_and_cleanup_tmp_dir

from lgd_tool.lgd_decompiler.LGC_reorganizer import (
    parse_lgc_functions,
    decide_segments,
    write_segment_files,
)


def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取实际的反编译文件，进行切分判定，并将提取的各个段落写出为临时 lgc 文件供审查。
    """
    content = load_tutorial_lgc_content()

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
    temp_output_dir = setup_temp_dir()

    print(f"步骤 3: 正在使用 write_segment_files 核心接口输出子 LGC 文件。临时输出目录:\n   {temp_output_dir}\n")
    write_segment_files(segments, temp_output_dir, "tutorial_00.lgc")

    wait_and_cleanup_tmp_dir(temp_output_dir)
    
    print("测试完毕。")


if __name__ == "__main__":
    run_manual_test()
