"""
global_var_processor.py

处理反编译后 LGC 文件的全局变量。
本文件包含了全局变量声明的提取解析、去重归约、局部特异冲突变量的分发注入、以及物理文件生成。
"""

from pathlib import Path
from lgd_tool.logger import logger
from lgd_tool.lgd_decompiler.LGC_reorganizer.export_processor import normalize_declaration_line


GLOBAL_VAR_START_MARKER = "// --- Global Variables ---"
GLOBAL_VAR_END_MARKER = "// =========================================="


def extract_globals_from_content(lgc_content: str) -> list[str]:
    """
    解析 LGC 文本内容，提取其中在首部区域定义的全部全局变量声明。

    :param lgc_content: 原始 LGC 文件的全部文本内容
    :return: 包含所有全局变量声明行的字符串列表（未归一化）
    """
    lines = lgc_content.splitlines()
    results = []

    # 1. 定位全局变量标记的起始行索引位置
    start_idx = 0
    for idx, line in enumerate(lines):
        if GLOBAL_VAR_START_MARKER in line:
            start_idx = idx + 1
            break

    # 2. 依次收集每一行，遇到格式改变或者结束标记时中断
    for idx in range(start_idx, len(lines)):
        line = lines[idx]
        text = line.strip()

        # 跳过空行
        if len(text) == 0:
            continue

        # 遇到结束标记则退出
        if text == GLOBAL_VAR_END_MARKER:
            break

        # 判断是否为全局变量行（以分号结束，且以 int 或 string 类型开头）
        is_global_var = False
        if text.endswith(";"):
            if text.startswith("int ") or text.startswith("string "):
                is_global_var = True

        if is_global_var:
            results.append(text)
        else:
            # 格式变化则直接退出
            break

    logger.debug("Extracted %d global variable lines", len(results))
    return results


def extract_variable_name(declaration: str) -> str:
    """
    从归一化后的全局变量声明行中提取其对应的变量名称。
    
    例如:
        "int SoundVolume;" -> "SoundVolume"
        "string musicAmbient = \"music\\\\mus00.ogg\";" -> "musicAmbient"
        "int AmmoPrice[11] = { 0 };" -> "AmmoPrice"

    :param declaration: 归一化后的全局变量声明行字符串
    :return: 提取出的变量名字字符串
    """
    clean_decl = declaration.strip()
    
    # 1. 去除数据类型前缀
    if clean_decl.startswith("int "):
        clean_decl = clean_decl[4:].strip()
    elif clean_decl.startswith("string "):
        clean_decl = clean_decl[7:].strip()
        
    # 2. 顺序过滤提取变量名字符，遇到空格、中括号、等号、分号时截止
    name_chars = []
    for char in clean_decl:
        if char == " " or char == "[" or char == "=" or char == ";":
            break
        name_chars.append(char)
        
    var_name = "".join(name_chars)
    return var_name.strip()


def process_global_variables(
    file_to_globals: dict[str, list[str]],
    output_dir: Path,
) -> dict[str, list[str]]:
    """
    对提取到的多个大文件的全局变量进行合并、分类和去重归一化。
    若变量在各文件中定义一致，则合流到公共全局变量 core/global_variable.lgc。
    若发生冲突（同名不同初始值等）或为独占变量，则将其划分给对应的私有注入映射。

    :param file_to_globals: 各大文件与其所含全局变量声明映射，格式为 { "tutorial_00.lgc": [变量声明行] }
    :param output_dir: 合并文件输出的物理根目录 Path
    :return: 每个大文件私有需要注入特异全局变量的映射字典，格式为 { "tutorial_00.lgc": [冲突私有变量声明行] }
    """
    # 1. 构建变量注册表，格式为 { 变量名: { 文件物理名: 归一化后的变量声明行 } }
    var_registry = {}

    for file_name, decl_lines in file_to_globals.items():
        for line in decl_lines:
            stripped = line.strip()
            if stripped != "":
                normalized = normalize_declaration_line(stripped)
                var_name = extract_variable_name(normalized)
                
                if var_name not in var_registry:
                    var_registry[var_name] = {}
                var_registry[var_name][file_name] = normalized

    public_globals = []
    
    # 初始化局部特异注入字典，避免使用字典推导式，采用平铺直叙的循环
    file_local_injections = {}
    for name in file_to_globals.keys():
        file_local_injections[name] = []

    # 2. 归类与分析每一个全局变量
    for var_name, occurrences in var_registry.items():
        unique_declarations = set(occurrences.values())
        
        # 只要没有发生初始值或定义的冲突，全部归类到公共全局变量列表
        if len(unique_declarations) == 1:
            # 列表中第一个也是唯一一个
            for val in unique_declarations:
                public_globals.append(val)
        else:
            # 发生定义/初始值冲突（例如：int var = 100; 与 int var = 10;）
            warning_detail = (
                f"[Global Merger] Global Var '{var_name}' have conflict or is exclusive between files\n"
                f"  -> Conflict/Exclusive distribution and details: \n"
                f"{occurrences}"
            )
            logger.warning(warning_detail)

            # 重新分发回各发生冲突文件的私有特异注入队列
            for file_name, decl_text in occurrences.items():
                file_local_injections[file_name].append(decl_text)

    # 3. 物理落盘写入到 core/global_variable.lgc 中
    output_globals_file = output_dir / "core" / "global_variable.lgc"
    write_global_variable_file(public_globals, output_globals_file)

    return file_local_injections


def write_global_variable_file(global_decls: list[str], output_path: Path) -> None:
    """
    将公共的全局变量声明列表物理写入 core/global_variable.lgc。
    并在文件头部引入防重复包含的 Sentinel 保护宏。

    :param global_decls: 归一化后的公共全局变量声明列表
    :param output_path: 目标写出物理文件 Path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_lines = []
    file_lines.append("#ifndef _CORE_GLOBAL_VARIABLE_LGC_")
    file_lines.append("#define _CORE_GLOBAL_VARIABLE_LGC_ aaa")
    file_lines.append("")
    file_lines.append(GLOBAL_VAR_END_MARKER)
    file_lines.append("// Public Global Variables")
    file_lines.append(f"// Total Variables: {len(global_decls)}")
    file_lines.append(GLOBAL_VAR_END_MARKER)
    file_lines.append("")
    
    for decl in global_decls:
        file_lines.append(decl)
        
    file_lines.append("")
    file_lines.append("#endif")
    file_lines.append("")
    
    content = "\n".join(file_lines)
    output_path.write_text(content, encoding="utf-8")
    logger.debug("Successfully wrote global variables with include guard to: %s", output_path)


# 兼容性命名定义，将测试用例中的变量归一化重定向到通用的 normalize_declaration_line
normalize_decl_text = normalize_declaration_line

