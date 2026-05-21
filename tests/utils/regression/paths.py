"""
Path helpers for LGC regression tests.

Pairing: ``lgd_files/regression_foo.lgd`` <-> ``regression_lgc/regression_foo.lgc``
(same basename, only extension differs).
"""

from pathlib import Path

from tests.conftest import (
    LGD_FILES_DIR,
    REGRESSION_LGC_DIR,
    REGRESSION_LGD_PREFIX,
    REGRESSION_OUTPUT_DIR,
)


def list_regression_lgd_files() -> list[Path]:
    """All regression inputs under ``lgd_files/`` (``regression_*.lgd``)."""
    files = sorted(LGD_FILES_DIR.glob(f"{REGRESSION_LGD_PREFIX}*.lgd"))
    return files


def expected_lgc_for_lgd(lgd_path: Path) -> Path:
    """
    Baseline LGC for a regression LGD file.

    e.g. ``regression_tutorial_00.lgd`` -> ``regression_lgc/regression_tutorial_00.lgc``
    """
    basename = lgd_path.name
    lgc_name = Path(basename).with_suffix(".lgc").name
    return REGRESSION_LGC_DIR / lgc_name


def regression_basename(lgd_path: Path) -> str:
    """Stem including prefix, e.g. ``regression_tutorial_00``."""
    return lgd_path.stem


def list_regression_pairs() -> list[tuple[Path, Path]]:
    """
    (lgd_path, expected_lgc_path) for each ``regression_*.lgd`` that has a baseline.
    """
    pairs = []
    for lgd_path in list_regression_lgd_files():
        expected = expected_lgc_for_lgd(lgd_path)
        if expected.exists():
            pairs.append((lgd_path, expected))
    return pairs


def work_dir_for_basename(basename: str) -> Path:
    """
    Runtime output directory for one case.

    ``basename`` is the full stem including prefix, e.g. ``regression_tutorial_00``.
    """
    return REGRESSION_OUTPUT_DIR / basename
