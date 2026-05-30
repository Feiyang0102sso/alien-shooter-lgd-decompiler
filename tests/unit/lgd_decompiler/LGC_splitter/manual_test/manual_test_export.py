"""
manual_test_export.py
"""

from manual_test_utils import load_tutorial_lgc_content, setup_temp_dir, wait_and_cleanup_tmp_dir

from lgd_tool.lgd_decompiler.LGC_reorganizer import (
    extract_extern_declarations,
    write_export_file,
)

def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取实际的 LGC 反编译文件，提取所有的 extern API 声明，并写出到临时 export 文件中供审查。
    """
    content = load_tutorial_lgc_content()

    # 调用 Export 提取模块
    print("正在从大 LGC 文件中匹配并提取 extern 函数...")
    externs = extract_extern_declarations(content)
    total_count = len(externs)
    print(f"-> 成功提取出 {total_count} 个 extern 声明。\n")

    if total_count == 173:
        print("【成功】提取数量完全吻合预期 (173/173)！\n")
    else:
        print(f"【失败】提取数量与预期不吻合！预期 173，实际 {total_count}。\n")

    # 产生临时文件夹
    temp_output_dir = setup_temp_dir()
    output_file = temp_output_dir / "export.lgc"
    write_export_file(externs, output_file)
    wait_and_cleanup_tmp_dir(temp_output_dir)

    print("测试完毕。")


if __name__ == "__main__":
    run_manual_test()
