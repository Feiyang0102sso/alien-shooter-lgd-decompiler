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


def lgd_path_for_regression_stem(stem: str) -> Path:
    """
    Resolve ``lgd_files/<stem>.lgd`` for a regression case stem.

    ``stem`` includes the ``regression_`` prefix, e.g. ``regression_tutorial_00``.
    """
    return LGD_FILES_DIR / f"{stem}.lgd"


def list_regression_lgd_for_stems(stems: list[str]) -> list[Path]:
    """LGD paths for the given regression case stems (order preserved)."""
    paths = []
    for stem in stems:
        paths.append(lgd_path_for_regression_stem(stem))
    return paths


def list_regression_pairs_for_stems(stems: list[str]) -> list[tuple[Path, Path]]:
    """
    (lgd_path, expected_lgc_path) for each stem in ``stems``.

    Used by LGC regression tests that enumerate an explicit case list
    (not every ``regression_*.lgd`` under fixtures).
    """
    pairs = []
    for stem in stems:
        lgd_path = lgd_path_for_regression_stem(stem)
        expected = expected_lgc_for_lgd(lgd_path)
        pairs.append((lgd_path, expected))
    return pairs


def list_regression_pairs() -> list[tuple[Path, Path]]:
    """
    (lgd_path, expected_lgc_path) for each ``regression_*.lgd`` that has a baseline.

    Prefer ``list_regression_pairs_for_stems`` when the test suite uses an explicit case list.
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
