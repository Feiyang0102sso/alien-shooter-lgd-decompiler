"""
__init__.py
"""

from .func_splitter import (
    LgcFunction,
    parse_lgc_functions,
    decide_segments,
    write_segment_files,
)
from .export_splitter import (
    extract_extern_declarations,
    write_export_file,
)
from .global_var_splitter import (
    extract_globals_from_content,
    write_global_variable_file,
)
from .merger import (
    normalize_declaration_line,
    verify_exports_strictly_identical,
    extract_variable_name,
    process_global_variables,
    LgcSegmentPool,
    merge_decompiled_project,
    split_and_backup_single_file,
    merge_and_backup_project,
    run_splitter_pipeline,
)

__all__ = [
    "LgcFunction",
    "parse_lgc_functions",
    "decide_segments",
    "write_segment_files",
    "extract_extern_declarations",
    "write_export_file",
    "extract_globals_from_content",
    "write_global_variable_file",
    "normalize_declaration_line",
    "verify_exports_strictly_identical",
    "extract_variable_name",
    "process_global_variables",
    "LgcSegmentPool",
    "merge_decompiled_project",
    "split_and_backup_single_file",
    "merge_and_backup_project",
    "run_splitter_pipeline",
]





