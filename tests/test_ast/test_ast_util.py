# test/test_ast/test_ast_util.py
from lgd_tool.lgd_decompiler.generate_LGC.asm_parser import AsmParser
from lgd_tool.lgd_decompiler.generate_LGC.cfg_builder import CFGBuilder
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import ASTBuilder


def parse_asm_methods(asm_path: str):
    """
    解析整个 ASM 文件，返回所有 Method 对象的列表。
    """
    parser = AsmParser()
    return parser.parse_file(asm_path)


def build_ast_for_method(method):
    """
    为单个 Method 对象构建 AST 并返回生成的语句列表。
    """
    cfg_builder = CFGBuilder()
    ast_builder = ASTBuilder()

    blocks = cfg_builder.build_cfg(method)

    all_statements = []
    for i, block in enumerate(blocks):
        is_last = (i == len(blocks) - 1)
        statements = ast_builder.build_block_ast(
            block,
            is_last_physical_block=is_last,
            method_name=method.name
        )
        all_statements.extend(statements)

    return all_statements