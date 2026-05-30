"""
manual_test_globals.py
"""

from manual_test_utils import load_tutorial_lgc_content, setup_temp_dir, wait_and_cleanup_tmp_dir
from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import (
    extract_globals_from_content,
    write_global_variable_file,
)

def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取实际的 LGC 反编译文件，提取所有的全局变量声明，并写出到临时全局变量文件中供审查。
    """
    content = load_tutorial_lgc_content()

    # 2. 调用全局变量提取模块
    print("正在从大 LGC 文件中匹配并提取全局变量声明...")
    globals_list = extract_globals_from_content(content)
    total_count = len(globals_list)
    print(f"-> 成功提取出 {total_count} 个全局变量声明。\n")

    # 3. 产生临时文件夹并输出以供直观验证
    temp_output_dir = setup_temp_dir()

    print(f"正在生成临时的 global_variable.lgc。临时输出目录:\n   {temp_output_dir}\n")

    output_file = temp_output_dir / "global_variable.lgc"
    write_global_variable_file(globals_list, output_file)
    wait_and_cleanup_tmp_dir(temp_output_dir)

    print("测试完毕。")


if __name__ == "__main__":
    run_manual_test()
