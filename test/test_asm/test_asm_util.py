"""
test/test_asm_util.py
ASM 测试专用的 helper 函数。
"""

import re

from core.context import LgdAnalysisContext
from core.parsers import P1LiteralParser, P2SymbolParser, FixedTableParser, BytecodeParser
from core.analyzer import LgdAnalyzer
from generate_intermediate.renderer_asm import LgdAsmRenderer


def run_pipeline_to_asm(lgd_path: str) -> tuple:
    """
    读取 lgd 文件，只运行到 ASM 生成为止。
    不调用 CSV / C / LGC 步骤。

    Returns:
        (ctx, asm_path)  —  LgdAnalysisContext 和生成的 .asm 文件路径
    """
    with open(lgd_path, "rb") as f:
        data = f.read()

    ctx = LgdAnalysisContext(
        file_path=lgd_path,
        file_size=len(data),
        raw_data=data,
    )

    # P1: Literal Table
    p1 = P1LiteralParser(data)
    ctx.literal_table, next_off = p1.parse(0)
    ctx.p1_offset_end = next_off

    # P2: Symbol Table
    p2 = P2SymbolParser(data)
    ctx.symbol_table, next_off = p2.parse(next_off)
    ctx.p2_offset_end = next_off

    # Fixed Tables: Action + ScriptEvent
    ft = FixedTableParser(data)
    ctx.action_tbl_offset_start = next_off
    ctx.action_table, next_off = ft.parse(next_off, "Action")
    ctx.action_tbl_offset_end = next_off

    ctx.event_tbl_offset_start = next_off
    ctx.script_event_table, next_off = ft.parse(next_off, "ScriptEvent")
    ctx.event_tbl_offset_end = next_off

    # Analyzer
    analyzer = LgdAnalyzer(ctx)
    analyzer.analyze()

    # Bytecode
    ctx.bytecode_offset_start = next_off
    bc = BytecodeParser(data)
    ctx.bytecode_instructions, _ = bc.parse(next_off)

    # ASM Renderer
    asm_path = lgd_path + ".asm"
    renderer = LgdAsmRenderer(ctx)
    renderer.render(asm_path)

    return ctx, asm_path


# LINE_NUM 操作数可能是十进制或十六进制（兼容旧版本输出）
_LINE_NUM_RE = re.compile(r"LINE_NUM\s+(0x[0-9A-Fa-f]+|\d+)")

# 匹配函数块：;Function Name() Begin ... ;Function Name() End
_FUNC_BLOCK_RE = re.compile(
    r";Function (.+?)\(\) Begin\r?\n(.*?);Function \1\(\) End",
    re.DOTALL,
)


def parse_asm_file(asm_path: str) -> list:
    """
    解析生成的 ASM 文件，提取每个函数的元数据。

    Returns:
        list of dict, 每个 dict 含：
            - name (str)
            - is_empty (bool)  —  函数体内无任何 LINE_NUM 时为 True
            - last_line_num (int|None)  —  最后一条 LINE_NUM 的操作数；空函数为 None
    """
    with open(asm_path, "r", encoding="utf-8") as f:
        content = f.read()

    results = []
    for m in _FUNC_BLOCK_RE.finditer(content):
        name = m.group(1)
        body = m.group(2)

        matches = _LINE_NUM_RE.findall(body)
        if matches:
            raw = matches[-1]
            last_line_num = int(raw, 16) if raw.startswith("0x") else int(raw)
            is_empty = False
        else:
            last_line_num = None
            is_empty = True

        results.append({
            "name": name,
            "is_empty": is_empty,
            "last_line_num": last_line_num,
        })

    return results
