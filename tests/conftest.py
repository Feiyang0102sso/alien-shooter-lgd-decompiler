"""
tests/conftest.py
Global Pytest Configuration and Common Path Constants.

Unified directory path for fixtures,
accessible by all test sub-packages.

CLI filters (see pyproject.toml):
  pytest                 — all tests
  pytest --unit          — tests/unit only
  pytest --regression    — tests/regression only
  (single-letter -u/-r are reserved by pytest 9+; optional: python -m tests.pytest_cli unit)
"""

from pathlib import Path

import pytest

# ===== Global Config =====
TESTS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = TESTS_DIR / "fixtures"

LGD_FILES_DIR = FIXTURES_DIR / "lgd_files"
EXPECTED_CSV_DIR = FIXTURES_DIR / "expected_csv"
ASM_FILES_DIR = FIXTURES_DIR / "asm_files"
GOLDEN_LGC_DIR = FIXTURES_DIR / "original_lgc"
REFINER_DB_DIR = FIXTURES_DIR / "refiner_db"

# LGC regression golden (see TEST_PLAN_LGC_REGRESSION.md)
REGRESSION_LGC_DIR = FIXTURES_DIR / "regression_lgc"
REGRESSION_LGD_PREFIX = "regression_"
REGRESSION_OUTPUT_DIR = TESTS_DIR / "output" / "regression_lgc"

# ===== Pytest suite paths (single source of truth for --unit / --regression and test-* scripts) =====
UNIT_TEST_REL_DIR = "tests/unit"
REGRESSION_TEST_REL_DIRS = ("tests/regression",)


def _path_for_filter(item_path) -> str:
    """Normalize test path to forward slashes for substring checks."""
    return item_path.as_posix()


def _path_matches_rel_dir(path_str: str, rel_dir: str) -> bool:
    """True if ``path_str`` is under ``rel_dir`` (forward-slash normalized)."""
    normalized = path_str.replace("\\", "/")
    needle = "/" + rel_dir + "/"
    return needle in normalized


def _is_unit_test_path(path_str: str) -> bool:
    return _path_matches_rel_dir(path_str, UNIT_TEST_REL_DIR)


def _is_regression_test_path(path_str: str) -> bool:
    for rel_dir in REGRESSION_TEST_REL_DIRS:
        if _path_matches_rel_dir(path_str, rel_dir):
            return True
    return False


def pytest_addoption(parser):
    """Add suite filters (--unit / --regression). Short -u/-r are reserved by pytest 9+."""
    parser.addoption(
        "--unit",
        action="store_true",
        default=False,
        help=f"Run only tests under {UNIT_TEST_REL_DIR}/",
    )
    parser.addoption(
        "--regression",
        action="store_true",
        default=False,
        help="Run only tests under: " + ", ".join(REGRESSION_TEST_REL_DIRS),
    )


def pytest_configure(config):
    unit_only = config.getoption("--unit")
    reg_only = config.getoption("--regression")
    if unit_only and reg_only:
        msg = "Use either --unit or --regression, not both"
        raise pytest.UsageError(msg)


def pytest_collection_modifyitems(config, items):
    unit_only = config.getoption("--unit")
    reg_only = config.getoption("--regression")
    if not unit_only and not reg_only:
        return

    kept = []
    dropped = []
    for item in items:
        path_str = _path_for_filter(item.path)
        keep = False
        if unit_only and _is_unit_test_path(path_str):
            keep = True
        if reg_only and _is_regression_test_path(path_str):
            keep = True
        if keep:
            kept.append(item)
        else:
            dropped.append(item)

    if dropped:
        config.hook.pytest_deselected(items=dropped)
    items[:] = kept
