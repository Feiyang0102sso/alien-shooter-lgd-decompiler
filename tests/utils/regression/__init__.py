"""
tests/utils/regression/

Utilities for LGC regression tests only (see TEST_PLAN_LGC_REGRESSION.md).
"""

from tests.utils.regression.lgc_compare import (
    LgcLine,
    compare_lgc_by_function,
    load_max_diff_lines,
    parse_lgc_functions,
)
from tests.utils.regression.while_issues_scan import (
    WhileIssue,
    count_error_issues,
    count_issues_by_type,
    scan_lgc_file,
)
from tests.utils.regression.paths import (
    expected_lgc_for_lgd,
    list_regression_pairs,
    list_regression_pairs_for_stems,
    lgd_path_for_regression_stem,
    regression_basename,
    work_dir_for_basename,
)

__all__ = [
    "WhileIssue",
    "count_error_issues",
    "count_issues_by_type",
    "scan_lgc_file",
    "LgcLine",
    "compare_lgc_by_function",
    "load_max_diff_lines",
    "parse_lgc_functions",
    "expected_lgc_for_lgd",
    "list_regression_pairs",
    "list_regression_pairs_for_stems",
    "lgd_path_for_regression_stem",
    "regression_basename",
    "work_dir_for_basename",
]
