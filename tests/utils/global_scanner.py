"""
global_scanner.py

测试辅助工具：扫描并分类统计反编译后 LGC 文件中的全局变量数据。
用于统计单个 LGC 文件中 int、string、int[]、string[] 全局变量各自的数量，并为自动化测试提供数据支持。
"""

import sys
from pathlib import Path

# 确保能加载 src 目录与项目根目录
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[1]
_SRC_DIR = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from lgd_tool.lgd_decompiler.LGC_splitter.global_var_splitter import extract_globals_from_content


def scan_globals_statistics(lgc_content: str) -> dict[str, int]:
    """
    扫描 LGC 源码文本，统计 int、string、int[]、string[] 四类全局变量各自的数量。

    参数:
        lgc_content: 包含 LGC 源码的完整文本。

    返回:
        一个统计字典，如 {"int": 10, "string": 5, "int[]": 2, "string[]": 1, "total": 18}。
    """
    global_lines = extract_globals_from_content(lgc_content)
    
    stats = {
        "int": 0,
        "string": 0,
        "int[]": 0,
        "string[]": 0,
        "total": 0
    }
    
    for line in global_lines:
        # 截取声明行在分号和赋值等号之前的前置核心部分
        decl_part = line.split("=")[0].split(";")[0].strip()
        
        is_array = "[" in decl_part
        
        if decl_part.startswith("int "):
            if is_array:
                stats["int[]"] += 1
            else:
                stats["int"] += 1
        elif decl_part.startswith("string "):
            if is_array:
                stats["string[]"] += 1
            else:
                stats["string"] += 1
                
    stats["total"] = len(global_lines)
    return stats


def run_main() -> None:
    """命令行运行的主入口，用于手动扫描并打印报告。"""
    # 回归测试文件的默认路径
    lgc_file_path = (
        _PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "regression_lgc"
        / "regression_tutorial_00.lgc"
    )
    
    if len(sys.argv) > 1:
        lgc_file_path = Path(sys.argv[1]).expanduser().resolve()
        
    if not lgc_file_path.exists():
        print(f"【错误】未找到 LGC 文件: {lgc_file_path}")
        sys.exit(1)
        
    print("=" * 70)
    print(f"正在扫描文件全局变量: {lgc_file_path.name}")
    print("=" * 70)
    
    content = lgc_file_path.read_text(encoding="utf-8", errors="replace")
    stats = scan_globals_statistics(content)
    
    print("全局变量分类统计报告如下:")
    print(f"  * int  (整型普通变量)   : {stats['int']:3d} 个")
    print(f"  * string (字符串普通变量) : {stats['string']:3d} 个")
    print(f"  * int[]  (整型数组变量)   : {stats['int[]']:3d} 个")
    print(f"  * string[] (字符串数组变量): {stats['string[]']:3d} 个")
    print("-" * 70)
    print(f"  * 累计全局变量总数 (total): {stats['total']:3d} 个")
    print("=" * 70)


if __name__ == "__main__":
    run_main()
