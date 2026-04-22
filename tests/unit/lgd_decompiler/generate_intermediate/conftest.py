"""
tests/unit/lgd_decompiler/generate_intermediate/conftest.py
session level fixture
auto cleaning generated .asm
"""

import pytest

from tests.conftest import LGD_FILES_DIR
from tests.utils.cleanup import wait_and_cleanup
from tests.utils.asm_helpers import run_pipeline_to_asm, parse_asm_file

EXCLUDE_LGD_FILES = {
    # (optional) may add exclude list here
    # not in EXCLUDE_LGD_FILES
}

INCLUDE_LGD_FILES = {
    "tutorial_00.lgd",
    "test_asm_empty.lgd",
    "test_asm_ret_only_1.lgd",
    "test_asm_ret_only_2.lgd",
    # (optional) may add include list here
    # in INCLUDE_LGD_FILES
}

# scan all .lgd and with the additional list
all_lgd = LGD_FILES_DIR.glob("*.lgd")
LGD_FILES = [p for p in all_lgd if p.name in INCLUDE_LGD_FILES]
LGD_NAMES = [p.name for p in LGD_FILES]


@pytest.fixture(scope="session", params=LGD_FILES, ids=LGD_NAMES)
def lgd_session(request):
    """
    run pipeline on each .lgd file

    Yields:
        (ctx, asm_path, asm_functions, lgd_name) tuple
    """
    current_lgd_path = request.param

    # Setup
    ctx, asm_path = run_pipeline_to_asm(str(current_lgd_path))
    asm_functions = parse_asm_file(asm_path)

    yield ctx, asm_path, asm_functions, current_lgd_path.name

    # Teardown
    wait_and_cleanup([asm_path])
