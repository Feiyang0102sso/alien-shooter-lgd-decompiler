"""
tests/utils/ast_helpers.py
AST builder helper

ASM parsing and AST construction
"""

from lgd_tool.lgd_decompiler.generate_LGC.asm_parser import AsmParser
from lgd_tool.lgd_decompiler.generate_LGC.cfg_builder import CFGBuilder
from lgd_tool.lgd_decompiler.generate_LGC.ast_builder import ASTBuilder


def parse_asm_methods(asm_path: str):
    """parse ASM file return method objects"""
    parser = AsmParser()
    return parser.parse_file(asm_path)


def build_ast_for_method(method):
    """
    build ast for single method

    Args:
        method: Method objects produced by AsmParser

    Returns:
        list: AST Statement Node List
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
