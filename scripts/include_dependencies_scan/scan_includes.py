"""
scan_includes.py

递归检测 LGC 脚本的 #include 依赖关系的分析工具。
支持：
- 给定主脚本，递归深挖它直接与间接包含的所有子脚本文件。
- 提供命令行包含路径参数 `-I`，自动在多个包含根目录以及同级目录中寻找物理文件。
- 全自动检测并警告循环依赖（Circular Dependency）。
- 绘制美观的缩进树形（Tree）结构以展现嵌套层次。
- 统计并去重列出所有被引用的唯一 LGC 文件列表及总数。
"""

import re
import sys
import argparse
from pathlib import Path
from typing import Optional, Set, List

# 将项目路径动态加入寻路，以便于无缝复用核心 LgcFunction 解析库
_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[1]  # 向上第 2 级为项目根目录 d:\python coding\lgd_tool
_SRC_DIR = _PROJECT_ROOT / "src"

if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from lgd_tool.lgd_decompiler.LGC_splitter import parse_lgc_functions

# ==================== 硬编码配置变量 ====================
# 要扫描的目标 LGC 文件路径（支持绝对或相对路径，Windows下首选前缀 r 以防斜杠转义）
# 可在此直接贴入您完整源码中的入口脚本路径
TARGET_LGC_PATH = r"D:\A-GameCenter\alien shooter\Alien Shooter Lost City 1.1.4 PC build + Code Leak\assets\maps - 副本\tutorial_00.lgc"

# 额外的 #include 依赖路径搜索文件夹目录列表（可添加多个。脚本会默认将 TARGET_LGC_PATH 所在文件夹作为搜索源之一）
INCLUDE_SEARCH_DIRS = [
    r"D:\A-GameCenter\alien shooter\Alien Shooter Lost City 1.1.4 PC build + Code Leak\assets\maps - 副本",
]
# ========================================================

# 匹配标准 #include 语句，例如 #include "core\export.lgc" 或 #include <common.lgc>
# 捕获组 1 包含实际写的相对文件路径
INCLUDE_PATTERN = re.compile(r"^\s*#include\s*[\"<]([^\"<>]+)[\">]")


class IncludeNode:
    """
    树节点数据结构，保存单个脚本及其被包含的子脚本列表。

    属性:
        file_path: 该脚本在磁盘上的绝对物理路径（如果成功找到）。
        rel_path_str: 写在 #include 指令中的原始字符串路径。
        depth: 嵌套层级深度，用于格式化缩进。
        children: 该文件直接包含的子节点列表。
        error: 如果文件丢失或发生循环引用，记录相关的错误或警告信息。
    """

    def __init__(
        self,
        rel_path_str: str,
        file_path: Optional[Path] = None,
        depth: int = 0,
    ) -> None:
        self.rel_path_str: str = rel_path_str
        self.file_path: Optional[Path] = file_path
        self.depth: int = depth
        self.children: List[IncludeNode] = []
        self.error: Optional[str] = None


def find_include_file(
    rel_path_str: str,
    current_file_dir: Path,
    search_roots: List[Path],
) -> Optional[Path]:
    """
    在当前文件所在目录以及各个指定的包含根目录中寻找 #include 的物理文件。

    参数:
        rel_path_str: 写在代码里的引用路径，例如 "core\\export.lgc"。
        current_file_dir: 当前处理的文件所在的文件夹 Path。
        search_roots: 从命令行传入的所有 -I 搜索根目录。

    返回:
        找到的物理绝对 Path，如未找到则返回 None。
    """
    # 统一斜杠，支持 Windows 和 Unix 格式的跨平台相互解析
    normalized_rel = rel_path_str.replace("\\", "/")

    # 1. 尝试以当前文件所在目录作为基准相对路径寻找
    try_current = current_file_dir / normalized_rel
    if try_current.is_file():
        return try_current.resolve()

    # 2. 依次在命令行传入的各个包含路径中寻找
    for root in search_roots:
        try_root = root / normalized_rel
        if try_root.is_file():
            return try_root.resolve()

    return None


def extract_includes_from_file(file_path: Path) -> List[str]:
    """
    快速读取一个 LGC 文件的内容并提取出所有合法的 #include 文件相对路径列表。

    参数:
        file_path: 目标 LGC 文件的物理 Path。

    返回:

        声明的包含引用字符串列表，保持出现顺序。
    """
    try:
        text = file_path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:
        # 如果读取失败，返回空
        return []

    includes = []
    lines = text.splitlines()
    for line in lines:
        stripped = line.strip()
        # 略过单行注释
        if stripped.startswith("//"):
            continue
        match = INCLUDE_PATTERN.match(line)
        if match is not None:
            raw_path = match.group(1).strip()
            includes.append(raw_path)

    return includes


def build_dependency_tree(
    rel_path_str: str,
    file_path: Optional[Path],
    depth: int,
    search_roots: List[Path],
    visited_paths: Set[Path],
) -> IncludeNode:
    """
    采用深度优先搜索（DFS）递归构建 LGC 文件的 #include 树，并进行环路检测。

    参数:
        rel_path_str: #include 中写的相对路径字符串。
        file_path: 该文件的绝对 Path（如尚未定位则传入 None 尝试寻找）。
        depth: 当前树节点深度。
        search_roots: 依赖搜索目录列表。
        visited_paths: 递归路径上已访问的文件集（用于阻断循环依赖）。

    返回:
        构建完成的依赖树节点 IncludeNode。
    """
    node = IncludeNode(rel_path_str=rel_path_str, file_path=file_path, depth=depth)

    # 1. 如果一开始没有传入物理路径，尝试定位它
    if node.file_path is None:
        # 当作根节点，在当前目录和搜索根目录搜索它
        node.file_path = find_include_file(
            rel_path_str=rel_path_str,
            current_file_dir=Path(".").resolve(),
            search_roots=search_roots,
        )

    # 2. 检查物理文件是否缺失
    if node.file_path is None:
        node.error = "文件未找到"
        return node

    # 3. 循环引用检测
    if node.file_path in visited_paths:
        node.error = "检测到循环引用 (Circular Include)"
        return node

    # 4. 读取文件，深挖它包含的子依赖项
    visited_paths.add(node.file_path)

    current_dir = node.file_path.parent
    sub_includes = extract_includes_from_file(node.file_path)

    for sub_rel in sub_includes:
        sub_physical = find_include_file(
            rel_path_str=sub_rel,
            current_file_dir=current_dir,
            search_roots=search_roots,
        )
        
        # 深度复制当前已访问的路径集合给子节点，以避免并列分支之间的伪循环报错
        sub_visited = set(visited_paths)
        
        child_node = build_dependency_tree(
            rel_path_str=sub_rel,
            file_path=sub_physical,
            depth=depth + 1,
            search_roots=search_roots,
            visited_paths=sub_visited,
        )
        node.children.append(child_node)

    return node


def collect_unique_files(node: IncludeNode, unique_paths: Set[Path]) -> None:
    """
    遍历整个依赖树，收集并去重所有成功定位的唯一物理文件。
    """
    if node.file_path is not None:
        unique_paths.add(node.file_path)

    for child in node.children:
        collect_unique_files(child, unique_paths)


def collect_file_max_depths(node: IncludeNode, depths_map: dict) -> None:
    """
    递归遍历依赖树，记录并更新每个唯一物理文件在依赖嵌套中所达到的最大深度 (Max Depth)。
    越是深层的公共库文件，其被引用的最大深度就越大。
    """
    if node.file_path is not None:
        path = node.file_path
        current_depth = node.depth
        if path not in depths_map:
            depths_map[path] = current_depth
        else:
            if current_depth > depths_map[path]:
                depths_map[path] = current_depth

    for child in node.children:
        collect_file_max_depths(child, depths_map)


def print_dependency_tree(node: IncludeNode) -> None:
    """
    美观地在控制台中以树状缩进格式打印整个递归 #include 嵌套树。
    """
    indent = "  " * node.depth
    
    if node.depth == 0:
        header = f"* [根节点] {node.rel_path_str}"
        if node.file_path is not None:
            header += f" ({node.file_path})"
        print(header)
    else:
        # 使用分支连线字符增加树状层级的清晰感，且完全保持 GBK 编码安全
        prefix = f"{indent}+-- "
        status_suffix = ""
        if node.error is not None:
            status_suffix = f"  <-- [!] [警告: {node.error}]"
        elif node.file_path is None:
            status_suffix = "  <-- [!] [错误: 找不到文件]"
            
        print(f"{prefix}{node.rel_path_str}{status_suffix}")

    for child in node.children:
        print_dependency_tree(child)


def main(argv: Optional[List[str]] = None) -> int:
    """
    命令行程序入口，解析参数，驱动递归分析，并汇总打印报告。
    """
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="分析 LGC 文件的 #include 树状递归依赖及统计。"
    )
    parser.add_argument(
        "script_path",
        nargs="?",
        default=None,
        help="目标主 LGC 脚本物理路径（如果不指定，自动执行脚本顶部的 TARGET_LGC_PATH 配置）",
    )
    parser.add_argument(
        "-I",
        "--include-dir",
        action="append",
        default=[],
        help="指定额外的 #include 搜索根目录，可多次声明指定多个路径（不指定则默认使用顶部的 INCLUDE_SEARCH_DIRS 配置）",
    )
    args = parser.parse_args(argv)

    # 1. 确定要扫描的目标主脚本物理路径（命令行传参优先，其次为文件顶部的硬编码值）
    raw_script_path = args.script_path
    if raw_script_path is None:
        raw_script_path = TARGET_LGC_PATH

    target_file = Path(raw_script_path).expanduser().resolve()
    if not target_file.is_file():
        print(f"[错误] 指定的目标主脚本不是合法的文件: {target_file}")
        print("请检查命令行传入参数或确认脚本顶部的 TARGET_LGC_PATH 是否配置正确。")
        return 1

    # 2. 整理搜索路径，将主脚本所在的目录自动默认作为搜索根路径之一
    search_roots: List[Path] = []
    search_roots.append(target_file.parent)
    
    # 3. 汇总包含搜索文件夹（命令行传参优先，其次为顶部的硬编码值列表）
    raw_include_dirs = args.include_dir
    if len(raw_include_dirs) == 0:
        raw_include_dirs = INCLUDE_SEARCH_DIRS
        
    for raw_dir in raw_include_dirs:
        dir_path = Path(raw_dir).expanduser().resolve()
        if dir_path.is_dir():
            search_roots.append(dir_path)
        else:
            print(f"[警告] 传入的搜索路径不存在或不是目录: {raw_dir}")

    print("=" * 80)
    print("                      LGC 递归 #include 依赖分析")
    print("=" * 80)
    print(f"目标主脚本: {target_file}")
    print(f"搜索目录集: {[str(r) for r in search_roots]}")
    print("-" * 80)

    # 2. 启动 DFS 递归解析树
    visited_set: Set[Path] = set()
    dependency_tree = build_dependency_tree(
        rel_path_str=target_file.name,
        file_path=target_file,
        depth=0,
        search_roots=search_roots,
        visited_paths=visited_set,
    )

    # 3. 打印依赖嵌套树
    print(">>> 嵌套依赖树状结构:")
    print_dependency_tree(dependency_tree)
    print("-" * 80)

    # 4. 统计并去重唯一外部包含的文件列表，进行精细化分类
    unique_paths: Set[Path] = set()
    collect_unique_files(dependency_tree, unique_paths)
    
    # 4.0 递归计算出每个唯一文件在整棵嵌套依赖树中所达到的最大嵌套深度 (Max Depth)
    depths_map = {}
    collect_file_max_depths(dependency_tree, depths_map)
    
    # 除去主脚本本身，剩余的就是所有被递归引入的其他不一样的外部依赖脚本文件
    if target_file in unique_paths:
        unique_paths.remove(target_file)

    # 声明三类依赖容器，包含其属性元组
    # h_files 存放元组: (path, max_depth)
    h_files = []
    # no_func_lgc 存放元组: (path, max_depth)
    no_func_lgc = []
    # has_func_lgc 存放元组: (path, method_count, max_depth)
    has_func_lgc = []

    # 遍历去重后的绝对物理路径列表进行类型与方法的提取判定
    for path in unique_paths:
        max_depth = depths_map.get(path, 0)
        
        if path.suffix.lower() == ".h":
            h_files.append((path, max_depth))
        else:
            # 读取该 LGC 文件，判断其内是否含有顶级函数定义并统计数量
            try:
                file_text = path.read_text(encoding="utf-8", errors="replace")
                parsed_funcs = parse_lgc_functions(file_text)
                method_count = len(parsed_funcs)
                if method_count > 0:
                    has_func_lgc.append((path, method_count, max_depth))
                else:
                    no_func_lgc.append((path, max_depth))
            except Exception:
                # 若读取解析异常，降级归入无方法文件
                no_func_lgc.append((path, max_depth))

    # 4.0.1 排序辅助函数，完全避开 lambda 表达式以确保高可读性与 KISS 原则
    def _sort_by_depth_desc(item) -> int:
        """获取元组中的 max_depth (即最后一项) 作为降序排序键值"""
        # 对于 h_files 与 no_func_lgc，格式是 (path, max_depth)，最后一项索引为 -1
        # 对于 has_func_lgc，格式是 (path, method_count, max_depth)，最后一项索引为 -1
        return item[-1]

    # 对各分类进行深度由深到浅（降序）排序，如果深度一致，默认保持字典序
    h_files.sort(key=_sort_by_depth_desc, reverse=True)
    no_func_lgc.sort(key=_sort_by_depth_desc, reverse=True)
    has_func_lgc.sort(key=_sort_by_depth_desc, reverse=True)

    print(f">>> 递归引入唯一外部依赖文件总数: {len(unique_paths)} 个")
    print("-" * 80)

    # 4.1 打印第一类：.h 头文件依赖
    print(f"1. [.h 头文件依赖] —— 共计: {len(h_files)} 个 (按依赖嵌套深度由深到浅排序):")
    if len(h_files) > 0:
        for idx, item in enumerate(h_files, start=1):
            path, max_depth = item
            print(f"  {idx:02d}. {path} (最大嵌套深度: {max_depth})")
    else:
        print("  (无)")
    print("")

    # 4.2 打印第二类：无方法的 lgc 脚本（仅包含全局变量定义或宏常量，不含顶级方法）
    print(f"2. [无方法的 lgc 脚本依赖 (纯数据/变量/配置)] —— 共计: {len(no_func_lgc)} 个 (按依赖嵌套深度由深到浅排序):")
    if len(no_func_lgc) > 0:
        for idx, item in enumerate(no_func_lgc, start=1):
            path, max_depth = item
            print(f"  {idx:02d}. {path} (最大嵌套深度: {max_depth})")
    else:
        print("  (无)")
    print("")

    # 4.3 打印第三类：有方法的其他 lgc 脚本（包含至少一个顶级方法定义）
    print(f"3. [有方法的其他 lgc 脚本依赖 (包含执行逻辑)] —— 共计: {len(has_func_lgc)} 个 (按依赖嵌套深度由深到浅排序):")
    if len(has_func_lgc) > 0:
        for idx, item in enumerate(has_func_lgc, start=1):
            path, method_count, max_depth = item
            print(f"  {idx:02d}. {path} (最大嵌套深度: {max_depth} | 包含顶级方法: {method_count} 个)")
    else:
        print("  (无)")
        
    print("=" * 80)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
