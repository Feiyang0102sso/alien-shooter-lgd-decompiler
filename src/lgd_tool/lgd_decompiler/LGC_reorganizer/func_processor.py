"""
func_processor.py

处理反编译后 LGC 文件的顶层函数段落与物理分块。
本文件包含了函数体边界的扫描提取（parse_lgc_functions）、基于反编译行号跳转的代码分块判定（decide_segments）、
单大文件直接分块写盘（write_segment_files）以及多文件普通段落的全局 MD5 哈希去重合并段池管理（LgcSegmentPool）。
"""

import re
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from lgd_tool.logger import logger

# 常量配置写在开头方便调试
# 用于匹配函数声明头的正则，例如 MyFunction(int a, string b)
FUNC_DECL_PATTERN = re.compile(r"^([A-Za-z0-9_]+)\s*\([^)]*\)\s*$")

# 用于排除的保留控制流关键字
RESERVED_KEYWORDS = frozenset(
    ("if", "else", "iff", "while", "for", "extern")
)

# 匹配反编译出的逻辑行号注释，例如 "// --- Line 965 ---"
LINE_COMMENT_PATTERN = re.compile(r"//\s*---\s*Line\s+(\d+)\s*---")


@dataclass
class LgcFunction:
    """
    存储反编译得出的 LGC 单个函数信息的结构体。

    Attributes:
        name: 函数名称
        start_line_idx: 在原始大 LGC 文本文件中的起始行索引值，自 0 开始
        lines: 该函数体包含的原始代码行列表
        min_line: 该函数体内部扫描到的最小逻辑行号，若为 None 代表空函数
        max_line: 该函数体内部扫描到的最大逻辑行号，若为 None 代表空函数
    """
    name: str
    start_line_idx: int
    lines: list[str]
    min_line: Optional[int] = None
    max_line: Optional[int] = None


def _fill_line_bounds(func: LgcFunction) -> None:
    """
    扫描并获取函数内含有的所有反编译行号注释，计算得出函数的最大与最小行号边界。

    :param func: 待计算边界信息的 LgcFunction 实例
    """
    found_lines = []
    for line in func.lines:
        match = LINE_COMMENT_PATTERN.search(line)
        if match is not None:
            raw_val = match.group(1)
            int_val = int(raw_val)
            found_lines.append(int_val)

    if len(found_lines) > 0:
        # 获取最值
        min_val = found_lines[0]
        max_val = found_lines[0]
        for val in found_lines:
            if val < min_val:
                min_val = val
            if val > max_val:
                max_val = val
        func.min_line = min_val
        func.max_line = max_val
    else:
        func.min_line = None
        func.max_line = None


def parse_lgc_functions(lgc_content: str) -> list[LgcFunction]:
    """
    解析 LGC 内容，并根据大括号匹配规则切分提取出所有的函数结构体。

    :param lgc_content: 原始 LGC 文本文件内容
    :return: 按照物理出现位置顺序排序的 LgcFunction 列表
    """
    lines = lgc_content.splitlines()
    functions = []

    in_func = False
    current_name = ""
    current_lines = []
    start_idx = 0
    brace_depth = 0

    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not in_func:
            match = FUNC_DECL_PATTERN.match(line)
            if match is not None:
                name = match.group(1)
                if name not in RESERVED_KEYWORDS:
                    current_name = name
                    current_lines = [line]
                    start_idx = idx
                    in_func = True
                    brace_depth = 0
            continue

        current_lines.append(line)
        brace_depth += line.count("{")
        brace_depth -= line.count("}")

        if brace_depth <= 0 and stripped == "}":
            func_obj = LgcFunction(
                name=current_name,
                start_line_idx=start_idx,
                lines=current_lines,
            )
            # 计算行号边界
            _fill_line_bounds(func_obj)
            functions.append(func_obj)

            # 复位判定状态
            in_func = False
            current_name = ""
            current_lines = []
            start_idx = 0
            brace_depth = 0

    return functions


def decide_segments(functions: list[LgcFunction]) -> dict[str, list]:
    """
    依据函数包含的逻辑行号变化，判定逻辑代码段发生“向后跳跃”的切分点。
    - 首个发生跳跃前的部分划归为 "export" 字段（后续用于前置引入）
    - 跳跃发生后的多个代码块存入 "segments"
    - 不包含有效行号的空函数自动跟随上一个活动段

    :param functions: 提取的 LgcFunction 函数列表
    :return: 包含 export 段与 segments 分割后段落列表的字典，格式为：
             { "export": [LgcFunction], "segments": [[LgcFunction], [LgcFunction]] }
    """
    segments = {"export": [], "segments": []}

    if len(functions) == 0:
        return segments

    has_jumped = False
    current_segment = []

    # 上一个正常行号最大的函数的 max_line
    prev_max = 0

    for func in functions:
        # 空函数无条件归于当前活动段
        if func.min_line is None or func.max_line is None:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)
            continue

        # 判断是否发生了后向逻辑跳跃（当前最小逻辑行号小于上个段最大的逻辑行号）
        if func.min_line < prev_max:
            has_jumped = True
            # 当已有段积累了内容，归档当前普通段，并重启一个新的分块
            if len(current_segment) > 0:
                segments["segments"].append(current_segment)
            current_segment = [func]
        else:
            if not has_jumped:
                segments["export"].append(func)
            else:
                current_segment.append(func)

        # 更新历史最大行号
        prev_max = func.max_line

    # 将剩余的所有普通函数块作为最后一个普通段归档
    if len(current_segment) > 0:
        segments["segments"].append(current_segment)

    return segments


def write_segment_files(
    segments: list[list[LgcFunction]],
    output_dir: Path,
) -> list[str]:
    """
    单大文件模式下直接物理将各个拆分出的普通段写入磁盘文件，统一命名为 segment_XX.lgc。
    注意：此函数仅写出传入的代码段列表，头部会自动注入 core 引用与哨兵包含保护。

    :param segments: 普通段列表（每个段是 LgcFunction 的列表）
    :param output_dir: 物理输出的目录 Path
    :return: 写入成功的普通段文件名列表
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    segment_filenames = []

    # 1. 物理写入各个普通的 segment_XX.lgc 段文件
    for idx, seg in enumerate(segments):
        seg_file_name = f"segment_{idx:02d}.lgc"
        segment_filenames.append(seg_file_name)
        seg_file = output_dir / seg_file_name

        # 构建 #ifndef 防重定义包含保护哨兵
        macro_name = f"_{seg_file_name.upper().replace('.', '_').replace('-', '_')}_"

        seg_lines = []
        seg_lines.append(f"#ifndef {macro_name}")
        seg_lines.append(f"#define {macro_name} aaa")
        seg_lines.append("")
        seg_lines.append("// ==========================================")
        seg_lines.append(f"// file {seg_file_name}")
        seg_lines.append("// references: 1")
        seg_lines.append("// ==========================================")
        seg_lines.append("")

        # 在所有的分段头部，全部前置引用核心导出及公共全局变量
        seg_lines.append('#include "core\\export.lgc"')
        seg_lines.append('#include "core\\global_variable.lgc"')
        seg_lines.append("")

        for func in seg:
            for line in func.lines:
                seg_lines.append(line)
            seg_lines.append("")

        seg_lines.append("#endif")
        seg_lines.append("")

        seg_file.write_text("\n".join(seg_lines), encoding="utf-8")
        logger.debug("Successfully wrote segment file with include guard to: %s", seg_file)

    return segment_filenames


class LgcSegmentPool:
    """
    管理多文件反编译分段的去重合并与指纹匹配机制（内存指纹池）。
    
    规则：
        - 对每个普通分段，在内存中将其下辖所有函数代码行物理拼接并消除换行符差异。
        - 计算拼接文本唯一的 MD5 哈希内容指纹，将其作为指纹池的 key 进行登记匹配。
        - 匹配成功：指纹已存在，跳过写盘，直接在物理引用依赖树上共享复用已有的物理文件名。
        - 匹配失败：分配一个新的按序命名的全局文件名（若发现重名，加后缀安全避让），物理落盘并在首部注入 #include。
    """

    def __init__(self, output_dir: Path):
        """
        初始化全局合并段池结构。

        :param output_dir: 去重合并后普通 LGC 段物理写出的目标根目录 Path
        """
        self.output_dir = output_dir
        # 全局去重哈希指纹池映射字典，格式为 { md5_hash: 共享物理文件名(如 "segment_01.lgc") }
        self.pool = {}
        # 已被占用分配的文件名集合，防止撞名安全避让
        self.assigned_filenames = set()
        # 记录各大原始文件分解出的普通分段所对应共享合并文件的有序引用链依赖树，格式为 { "level_01.lgc": ["segment_01.lgc", "segment_02.lgc"] }
        self.file_references = {}
        # 保存段落对应的物理源码文本内容，用于延迟统一写盘，格式为 { 物理文件名: 段落源码文本 }
        self.segment_contents = {}
        # 统计段落被引用的实际次数，格式为 { 物理文件名: 引用次数 }
        self.segment_ref_counts = {}

    def register_file_segments(self, file_name: str, segments: list[list[LgcFunction]]) -> None:
        """
        将某个原始大文件切分出来的普通分段列表，按原物理时序位置，在全局哈希池中去重登记并生成有序共享依赖文件名序列。

        :param file_name: 原始大文件在工程中的相对物理名称（如 "level_01.lgc"）
        :param segments: 该大文件切分出的普通代码分段（已剥离最后一个主逻辑段）列表
        """
        self.file_references[file_name] = []

        for idx, seg_funcs in enumerate(segments):
            # 1. 拼接段内包含的所有函数的原始代码行，用空行隔开
            lines_list = []
            for func in seg_funcs:
                func_text = "\n".join(func.lines)
                lines_list.append(func_text)
            
            seg_content = "\n\n".join(lines_list)
            
            # 统一换行符，去除由于平台或反编译差异带来的物理换行符干扰，确保哈希一致
            normalized_content = seg_content.replace("\r\n", "\n")
            seg_hash = hashlib.md5(normalized_content.encode("utf-8")).hexdigest()

            # 2. 判断指纹库中是否已存在内容完全对称一致的段
            if seg_hash in self.pool:
                existing_filename = self.pool[seg_hash]
                
                # 指纹一致，直接将其已有物理文件名关联入该文件的依赖链，完成无损合并
                self.file_references[file_name].append(existing_filename)
                
                # 累加实际的引用次数
                self.segment_ref_counts[existing_filename] = self.segment_ref_counts.get(existing_filename, 0) + 1
                
                logger.debug(
                    f"[SEGMENT MATCH] file '{file_name}' match {idx + 1} contents "
                    f"combined successfully with '{existing_filename}'"
                )
            else:
                # 3. 产生未曾录入的新段，安全分配合并文件名
                desired_name = f"segment_{len(self.pool):02d}.lgc"

                # 4. 安全阀撞名避让逻辑
                suffix_idx = 1
                base_stem = Path(desired_name).stem
                while desired_name in self.assigned_filenames:
                    desired_name = f"{base_stem}_{suffix_idx:03d}.lgc"
                    suffix_idx += 1

                # 5. 登记并绑定分配关系
                self.pool[seg_hash] = desired_name
                self.assigned_filenames.add(desired_name)
                self.file_references[file_name].append(desired_name)

                # 将新段的源码内容和引用计数暂存在内存中，等待所有关卡文件注册完后统一写入
                self.segment_contents[desired_name] = seg_content
                self.segment_ref_counts[desired_name] = 1
                
                logger.debug(
                    f"[SEGMENT NEW] New segment found, write into {desired_name}"
                )

    def _write_segment_to_disk(self, file_name: str, content: str, ref_count: int = 0) -> None:
        """
        物理落盘合并去重后的普通段落脚本，在其头部自动内联 core/export.lgc 及 core/global_variable.lgc，
        并包裹 #ifndef / #define 哨兵宏来屏蔽引擎二次载入重定义的编译错误。
        同时在注释中写入此普通段落被引用的实际次数。

        :param file_name: 写出的目标物理文件名
        :param content: 该段拼接的原始函数代码体文本
        :param ref_count: 该普通代码段最终被各源文件引用的累计次数
        """
        out_path = self.output_dir / file_name
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # 归一化宏名称，例如 segment_01.lgc -> _SEGMENT_01_LGC_
        macro_name = f"_{file_name.upper().replace('.', '_').replace('-', '_')}_"

        file_lines = []
        file_lines.append(f"#ifndef {macro_name}")
        file_lines.append(f"#define {macro_name} aaa")
        file_lines.append("")
        file_lines.append("// ==========================================")
        file_lines.append(f"// file {file_name}")
        file_lines.append(f"// references: {ref_count}")
        file_lines.append("// ==========================================")
        file_lines.append("")

        # 在所有的分段头部，全部前置引用核心导出及公共全局变量
        file_lines.append('#include "core\\export.lgc"')
        file_lines.append('#include "core\\global_variable.lgc"')
        file_lines.append("")

        file_lines.append(content)
        file_lines.append("")
        file_lines.append("#endif")
        file_lines.append("")

        out_path.write_text("\n".join(file_lines), encoding="utf-8")

    def write_all_segments(self) -> None:
        """
        在所有大文件都注册并统计完毕后，统一将内存中去重合并后的所有普通代码分段物理写出到磁盘中。
        此时可以精准获取并写入每个 segment 最终在多文件间的真实被引用次数。
        """
        for file_name, content in self.segment_contents.items():
            ref_count = self.segment_ref_counts.get(file_name, 0)
            self._write_segment_to_disk(file_name, content, ref_count)
            logger.debug(f"[SEGMENT NEW] Successfully wrote unique segment: {file_name} (ref count: {ref_count})")
