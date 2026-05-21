"""
Work directory helpers for LGC regression tests.

Runs ``LgdPipeline`` inside ``tests/output/regression_lgc/<basename>/`` so fixtures
are not polluted with ``.asm`` / ``.csv`` siblings.
"""

import shutil
from pathlib import Path

from lgd_tool.lgd_decompiler.core.pipeline import LgdPipeline

from tests.utils.regression.paths import work_dir_for_basename

INPUT_LGC_NAME = "input.lgc"
ON_FAILURE_DIR_NAME = "on_failure"
FAILURE_REPORT_NAME = "diff_report.txt"


def prepare_work_dir(basename: str) -> Path:
    """
    Create a clean work directory for one regression case.

    ``basename`` is the full stem, e.g. ``regression_tutorial_00``.
    """
    work_dir = work_dir_for_basename(basename)
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    return work_dir


def copy_lgd_into_work_dir(lgd_path: Path, work_dir: Path) -> Path:
    """Copy the fixture LGD into the work directory; keep the original filename."""
    dest = work_dir / lgd_path.name
    shutil.copy2(lgd_path, dest)
    return dest


def run_pipeline_in_work_dir(work_lgd_path: Path) -> Path:
    """
    Run the full decompiler pipeline on ``work_lgd_path``.

    Returns the path to the generated ``.lgc`` (same stem as the LGD).
    """
    pipeline = LgdPipeline(str(work_lgd_path))
    pipeline.run(keep_intermediate=False)

    lgc_path = work_lgd_path.with_suffix(".lgc")
    if not lgc_path.exists():
        msg = f"Pipeline did not produce LGC: {lgc_path}"
        raise FileNotFoundError(msg)

    return lgc_path


def finalize_actual_lgc(work_dir: Path, generated_lgc: Path) -> Path:
    """
    Rename generated LGC to ``input.lgc`` and remove other files in ``work_dir``.

    Returns the path to ``input.lgc``.
    """
    input_lgc = work_dir / INPUT_LGC_NAME

    if input_lgc.exists():
        input_lgc.unlink()

    generated_lgc.rename(input_lgc)

    for child in work_dir.iterdir():
        if child.name == INPUT_LGC_NAME:
            continue
        if child.is_dir():
            shutil.rmtree(child)
        else:
            child.unlink()

    return input_lgc


def remove_work_dir(work_dir: Path) -> None:
    """Delete the entire work directory (passing case)."""
    if work_dir.exists():
        shutil.rmtree(work_dir)


def write_failure_report(work_dir: Path, report_text: str) -> Path:
    """Persist diff details under ``on_failure/`` for debugging."""
    on_failure_dir = work_dir / ON_FAILURE_DIR_NAME
    on_failure_dir.mkdir(parents=True, exist_ok=True)
    report_path = on_failure_dir / FAILURE_REPORT_NAME
    report_path.write_text(report_text, encoding="utf-8")
    return report_path
