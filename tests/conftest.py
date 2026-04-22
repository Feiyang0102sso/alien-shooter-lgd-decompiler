"""
tests/conftest.py
Global Pytest Configuration and Common Path Constants.

Unified directory path for fixtures,
accessible by all test sub-packages.
"""

from pathlib import Path

# ===== Global Config =====
TESTS_DIR = Path(__file__).resolve().parent
FIXTURES_DIR = TESTS_DIR / "fixtures"

LGD_FILES_DIR = FIXTURES_DIR / "lgd_files"
EXPECTED_CSV_DIR = FIXTURES_DIR / "expected_csv"
ASM_FILES_DIR = FIXTURES_DIR / "asm_files"
GOLDEN_LGC_DIR = FIXTURES_DIR / "original_lgc"
REFINER_DB_DIR = FIXTURES_DIR / "refiner_db"
