"""
__init__.py
"""

from .splitter_core import (
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

__all__ = [
    "LgcFunction",
    "parse_lgc_functions",
    "decide_segments",
    "write_segment_files",
    "extract_extern_declarations",
    "write_export_file",
    "extract_globals_from_content",
    "write_global_variable_file",
]
