"""
tests/regression/lgc/test_lgc_regression.py

LGC regression: decompile ``regression_*.lgd`` and compare function bodies line-by-line
against ``regression_lgc/regression_*.lgc`` baselines.

See TEST_PLAN_LGC_REGRESSION.md.
"""

import pytest

from tests.utils.regression.lgc_compare import (
    compare_lgc_by_function,
    format_compare_failure,
    load_max_diff_lines,
)
from tests.utils.regression.paths import (
    expected_lgc_for_lgd,
    list_regression_lgd_files,
    list_regression_pairs,
    regression_basename,
)
from tests.utils.regression.workdir import (
    copy_lgd_into_work_dir,
    finalize_actual_lgc,
    prepare_work_dir,
    remove_work_dir,
    run_pipeline_in_work_dir,
    write_failure_report,
)


def _collect_regression_case_ids():
    """Pytest ids: basename strings for parametrized cases."""
    ids = []
    for lgd_path, _expected in list_regression_pairs():
        ids.append(regression_basename(lgd_path))
    return ids


_REGRESSION_PAIRS = list_regression_pairs()
_REGRESSION_IDS = _collect_regression_case_ids()


@pytest.mark.parametrize(
    "lgd_path,expected_lgc_path",
    _REGRESSION_PAIRS,
    ids=_REGRESSION_IDS,
)
def test_lgc_regression_matches_baseline(lgd_path, expected_lgc_path):
    """
    Decompile one regression LGD and assert function bodies match the golden LGC.
    """
    basename = regression_basename(lgd_path)
    max_diff_lines = load_max_diff_lines(basename, default=0)

    work_dir = prepare_work_dir(basename)

    try:
        work_lgd = copy_lgd_into_work_dir(lgd_path, work_dir)
        generated_lgc = run_pipeline_in_work_dir(work_lgd)

        expected_text = expected_lgc_path.read_text(encoding="utf-8")
        actual_text = generated_lgc.read_text(encoding="utf-8")

        result = compare_lgc_by_function(
            expected_text,
            actual_text,
            max_diff_lines=max_diff_lines,
        )

        input_lgc = finalize_actual_lgc(work_dir, generated_lgc)

        if result.passed:
            remove_work_dir(work_dir)
            return

        report = format_compare_failure(
            function_diffs=result.function_diffs,
            missing_functions=result.missing_functions,
            extra_functions=result.extra_functions,
            max_diff_lines=max_diff_lines,
            total_mismatches=(
                len(result.missing_functions)
                + len(result.extra_functions)
                + len(result.function_diffs)
            ),
            case_name=basename,
            work_dir=work_dir,
        )
        write_failure_report(work_dir, report)

        pytest.fail(report)

    except Exception:
        # Leave work_dir contents for inspection when pipeline or IO fails
        raise


def test_all_regression_lgd_have_baseline():
    """
    Every ``regression_*.lgd`` under fixtures must have a matching ``.lgc`` baseline.
    """
    missing = []
    for lgd_path in list_regression_lgd_files():
        expected = expected_lgc_for_lgd(lgd_path)
        if not expected.exists():
            missing.append(f"{lgd_path.name} -> {expected.name}")

    assert not missing, (
        "Missing regression LGC baselines:\n  " + "\n  ".join(missing)
    )
