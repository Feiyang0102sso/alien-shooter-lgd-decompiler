"""
manual_test_export_merger.py

用于手动直观测试 LGC 拆分器中 Export 合并比对与强熔断机制的测试脚本。
该脚本读取真实的回归测试文件，并制造不同的一致性状态，直观向用户演示：
1. 正常一致性状态下的 100% 自动合并写盘。
2. 数量不一致状态下的 logger.error 诊断和 sys.exit 进程终止行为。
3. 内容/顺序不一致状态下的 logger.error 诊断和 sys.exit 进程终止行为。
并在完成演示后提供一键临时目录擦除清理。
"""

import sys
import shutil
from pathlib import Path

# 将项目根目录与 src 目录加入 Python 寻找路径，以便能正常导入我们的核心库
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[3]
_SRC_DIR = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from lgd_tool.lgd_decompiler.LGC_splitter import (
    extract_extern_declarations,
    write_export_file,
    verify_exports_strictly_identical,
)


def run_manual_test() -> None:
    """
    手动测试的主要逻辑函数。
    读取真实的回归测试大文件，人为伪造多文件合并场景，分阶段直观展示合并器的强健性。
    """
    print("=" * 80)
    print("【手动测试】LGC 多文件 Export 合并去重与原序严苛比对工具")
    print("=" * 80)

    # 1. 读取真实回归文件作为基准数据源
    lgc_file_path = (
        _PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "regression_lgc"
        / "regression_tutorial_00.lgc"
    )

    if not lgc_file_path.exists():
        print(f"[错误] 未找到真实的回归测试大文件: {lgc_file_path}")
        return

    print(f"正在从真实文件提取基础 Export API 集合: {lgc_file_path.name}")
    raw_content = lgc_file_path.read_text(encoding="utf-8", errors="replace")
    base_externs = extract_extern_declarations(raw_content)
    print(f"-> 基准文件提取了 {len(base_externs)} 条 extern 声明。\n")

    # 产生临时测试目录
    temp_dir = _CURRENT_DIR / "_manual_merger_temp"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True, exist_ok=True)

    # =========================================================================
    # 演示 1：正常一致性状态下的合并写盘
    # =========================================================================
    print("-" * 80)
    print("【演示阶段 1】正常且完全一致的多文件 Export 合并...")
    print("-" * 80)

    # 模拟两关的 export，完全一致（仅内部排版空格略有不同）
    file_to_exports_ok = {
        "addon0/level_01.lgc": base_externs,
        "addon0/level_02.lgc": [f"   {decl}   " for decl in base_externs],
    }

    try:
        clean_decls = verify_exports_strictly_identical(file_to_exports_ok)
        print("-> [成功] 一致性校验顺利通过！")
        
        output_export_file = temp_dir / "core" / "export.lgc"
        write_export_file(clean_decls, output_export_file)
        
        if output_export_file.exists():
            print(f"-> [成功] 公共 Export 文件顺利生成: {output_export_file.relative_to(_PROJECT_ROOT)}")
            print(f"   物理大小: {output_export_file.stat().st_size} 字节，共 {len(clean_decls)} 条归一化 API。")
    except SystemExit:
        print("-> [意外失败] 一致的数据在校验时竟然触发了进程熔断！")

    # =========================================================================
    # 演示 2：数量不一致时的强行熔断
    # =========================================================================
    print("\n" + "-" * 80)
    print("【演示阶段 2】数量不一致时的进程强行熔断测试...")
    print("-" * 80)
    print("我们将故意让第二关的 export 缺失最后一条，观察合并器是否会抛出红色错误并强退。")
    
    # 故意使第二关缺失最后一条 extern 声明
    level_02_bad_len = base_externs[:-1]
    
    file_to_exports_bad_len = {
        "addon0/level_01.lgc": base_externs,
        "addon0/level_02.lgc": level_02_bad_len,
    }

    try:
        # 下述代码一定会触发 sys.exit 强退
        verify_exports_strictly_identical(file_to_exports_bad_len)
        print("-> [失败] 严重漏洞！数量不一致竟然通过了校验！")
    except SystemExit as e:
        print(f"\n-> [完美拦截] 进程被成功熔断！系统强行抛出了 SystemExit 信号，状态码为: {e.code}")

    # =========================================================================
    # 演示 3：内容/顺序不一致时的强行熔断
    # =========================================================================
    print("\n" + "-" * 80)
    print("【演示阶段 3】内容/物理顺序不一致时的进程强行熔断测试...")
    print("-" * 80)
    print("我们将故意让第二关的第 5 条 extern 声明与第一关存在一字节的微小差异，观察精准的行冲突日志。")

    level_02_bad_content = list(base_externs)
    # 人为修改第 5 条 (索引 4) 的声明内容
    level_02_bad_content[4] = level_02_bad_content[4] + " // 这是一个微小的不一致冲突"

    file_to_exports_bad_content = {
        "addon0/level_01.lgc": base_externs,
        "addon0/level_02.lgc": level_02_bad_content,
    }

    try:
        verify_exports_strictly_identical(file_to_exports_bad_content)
        print("-> [失败] 严重漏洞！内容不一致竟然通过了校验！")
    except SystemExit as e:
        print(f"\n-> [完美拦截] 进程被成功熔断！系统强行抛出了 SystemExit 信号，状态码为: {e.code}")

    # =========================================================================
    # 手动测试收尾，擦除物理垃圾
    # =========================================================================
    print("\n" + "=" * 80)
    print("手动测试演示完毕！")
    print(f"您可以查看生成的临时目录: {temp_dir.relative_to(_PROJECT_ROOT)}")
    print("=" * 80)

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
