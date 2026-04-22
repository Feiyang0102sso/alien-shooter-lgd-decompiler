"""
tests/unit/lgd_decompiler/generate_LGC/conftest.py
session level fixture

- ast_method_session: build ast (ifdef recovery, assignment pattern...)
- lgc_session: build lgc (unstatic array...)
"""

import pytest

from tests.conftest import ASM_FILES_DIR
from tests.utils.ast_helpers import parse_asm_methods, build_ast_for_method
from tests.utils.lgc_helpers import generate_and_read_lgc

# ===== ast_method_session =====
AST_ASM_FILE = ASM_FILES_DIR / "test_stack_in_ifdef.lgd.asm"


def _get_all_methods():
    if not AST_ASM_FILE.exists():
        return []
    return parse_asm_methods(str(AST_ASM_FILE))


METHODS = _get_all_methods()
METHOD_NAMES = [m.name for m in METHODS]


@pytest.fixture(scope="session", params=METHODS, ids=METHOD_NAMES)
def ast_method_session(request):
    """
    build AST for each method

    Yields:
        (method_name, statements) tuple
    """
    method = request.param
    statements = build_ast_for_method(method)
    yield method.name, statements


# ===== lgc_session =====
# INCLUDE_ASM_FILES = {
#     "test_loc_unstatic_arr.lgd.asm",
#     # (optional) may add include list here
#     # in INCLUDE_LGD_FILES
# }

LGC_ASM_FILES = list(ASM_FILES_DIR.glob("*.lgd.asm"))
LGC_ASM_NAMES = [p.name for p in LGC_ASM_FILES]


@pytest.fixture(scope="session", params=LGC_ASM_FILES, ids=LGC_ASM_NAMES)
def lgc_session(request):
    """
    build LGC pipeline

    Yields:
        (content, asm_name) tuple
    """
    asm_path = request.param

    base_name = asm_path.stem  # e.g. test_loc_unstatic_arr.lgd
    csv_path = asm_path.with_name(f"{base_name}.csv")

    prefix = asm_path.name.split('.')[0]
    output_lgc_path = ASM_FILES_DIR / f"{prefix}_output.lgc"

    # Setup
    content = generate_and_read_lgc(asm_path, csv_path, output_lgc_path)

    yield content, asm_path.name

    # Teardown
    if output_lgc_path.exists():
        output_lgc_path.unlink()
