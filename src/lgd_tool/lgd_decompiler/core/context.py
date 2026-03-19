"""
core/context.py
"""

from dataclasses import dataclass, field
from typing import List, Dict
from lgd_tool.lgd_decompiler.common.structures import P1LiteralEntry, P2SymbolEntry, SpecialEntry, BytecodeEntry


@dataclass
class LgdAnalysisContext:
    """
    Save all status data during the decompilation
    Subsequent both work based on this Context
    Analyzer and Renderer and so on
    """

    # initial raw data
    file_path: str
    file_size: int
    raw_data: bytes

    # Parsed raw data
    literal_table: List[P1LiteralEntry] = field(default_factory=list)
    symbol_table: List[P2SymbolEntry] = field(default_factory=list)

    # analyzed correlation data (populated by Analyzer.py)
    # Mapping: Literal Index -> Symbol Entry
    idx_to_symbol: Dict[int, P2SymbolEntry] = field(default_factory=dict)

    # Mapping: Literal Index -> Argument Comment (e.g. "// [Arg 1]")
    arg_split_map: Dict[int, str] = field(default_factory=dict)

    # Mapping: Literal Index -> Parameter Name (e.g. "para1")
    extern_para_map: Dict[int, str] = field(default_factory=dict)

    # List of defined entries (we can ignore 0xFFFFFFFF ones to save memory)
    action_table: List[SpecialEntry] = field(default_factory=list)
    script_event_table: List[SpecialEntry] = field(default_factory=list)

    # for logging info
    p1_offset_start: int = 0
    p1_offset_end: int = 0
    p2_offset_start: int = 0
    p2_offset_end: int = 0

    action_tbl_offset_start: int = 0
    action_tbl_offset_end: int = 0
    event_tbl_offset_start: int = 0
    event_tbl_offset_end: int = 0

    # Bytecode starts after these tables
    bytecode_offset_start: int = 0
    bytecode_instructions: List[BytecodeEntry] = field(default_factory=list)

    # versioning
    is_old_version: bool = False