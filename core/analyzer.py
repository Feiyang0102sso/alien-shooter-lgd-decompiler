"""
core/analyzer.py
"""

from logger import logger
from common.definitions import LgdDefinitions
from core.context import LgdAnalysisContext


class LgdAnalyzer:
    def __init__(self, context: LgdAnalysisContext):
        self.ctx = context

    def analyze(self):
        """execute all analyzer functions"""
        self._map_indices()
        self._analyze_extern_params()
        self._analyze_script_args()
        self._analyze_global_ids()
        self._analyze_special_tables()
        logger.debug("[Analyzer] Relationship analysis completed.")

    def _map_indices(self):
        """Establish a mapping from Literal Index to Symbol"""
        self.ctx.idx_to_symbol = {sym.p1_idx: sym for sym in self.ctx.symbol_table}

    def _analyze_extern_params(self):
        """Identify parameter placeholders for Extern functions"""
        for sym in self.ctx.symbol_table:
            t_base = sym.type_val & 0xFF
            if t_base == LgdDefinitions.BASE_EXTERN:
                start = sym.p1_idx
                for k in range(sym.size):
                    # write into Context
                    self.ctx.extern_para_map[start + k] = f"para{k + 1}"

    def _analyze_script_args(self):
        """Add separators to script function parameters"""
        for sym in self.ctx.symbol_table:
            t_base = sym.type_val & 0xFF
            if t_base == LgdDefinitions.BASE_FUNCTION:
                start_idx = sym.p1_idx
                end_limit = start_idx + sym.size
                current_idx = start_idx
                arg_counter = 1

                while current_idx < end_limit and current_idx < len(self.ctx.literal_table):
                    entry = self.ctx.literal_table[current_idx]

                    # Use Offset to get accurate Flag Info
                    info = LgdDefinitions.get_flag_info(entry.flag, offset=entry.offset)

                    count = entry.id_size
                    is_array = "array" in info.get('mode', '')

                    comment = f"// [Arg {arg_counter}]"
                    step = count if (is_array and count > 1) else 1

                    # write into Context
                    self.ctx.arg_split_map[current_idx] = comment

                    current_idx += step
                    arg_counter += 1

    def _analyze_global_ids(self):
        """
        Calculates GlobalID based on Symbol intervals.
        Logic: The range of a GlobalID is from the p1_idx of the current symbol
               to the p1_idx of the next symbol.
        """
        # 1. Filter and sort the symbol table (only take valid symbols that point to table P1).
        # Use <= instead of < to ensure empty functions at the very end are included
        valid_symbols = [s for s in self.ctx.symbol_table if s.p1_idx <= len(self.ctx.literal_table)]
        sorted_symbols = sorted(valid_symbols, key=lambda s: s.p1_idx)

        global_counter = 0
        total_p1_rows = len(self.ctx.literal_table)

        for i, sym in enumerate(sorted_symbols):
            start_idx = sym.p1_idx

            # Determine the end position of the current group (i.e., the start position of the next group).
            if i + 1 < len(sorted_symbols):
                end_idx = sorted_symbols[i + 1].p1_idx
            else:
                end_idx = total_p1_rows  # The last symbol until the end of the file

            # safety check
            if start_idx >= total_p1_rows: continue
            # add calculation based on actual size
            sym.actual_size = end_idx - start_idx

            # 2. Batch assignment GlobalID
            # All rows P1 within this interval
            # (including array elements, function parameters, and local variables) belong to this ID.
            for k in range(start_idx, end_idx):
                self.ctx.literal_table[k].global_id = global_counter
                self.ctx.literal_table[k].is_group_head = (k == start_idx)

            global_counter += 1

    def _analyze_special_tables(self):
        """
        [New] Log ActionX / ScriptEventX entries and their offset ranges.
        """
        # --- 1. Action Table Analysis ---
        a_start = self.ctx.action_tbl_offset_start
        a_end = self.ctx.action_tbl_offset_end

        logger.info(f"[Analyzer] === Action Table (Offset: 0x{a_start:X} - 0x{a_end:X}) ===")

        if not self.ctx.action_table:
            logger.info("    -> No Actions defined (All 0xFFFFFFFF).")
        else:
            for entry in self.ctx.action_table:
                # P1 Index
                logger.info(f"    -> Action{entry.slot_id:<3} linked to P1_Index: {entry.raw_val}")

        # --- 2. ScriptEvent Table Analysis ---
        e_start = self.ctx.event_tbl_offset_start
        e_end = self.ctx.event_tbl_offset_end

        logger.info(f"[Analyzer] === ScriptEvent Table (Offset: 0x{e_start:X} - 0x{e_end:X}) ===")

        if not self.ctx.script_event_table:
            logger.info("    -> No ScriptEvents defined (All 0xFFFFFFFF).")
        else:
            for entry in self.ctx.script_event_table:
                #  Global ID
                logger.info(f"    -> ScriptEvent{entry.slot_id:<3} linked to Global_ID: {entry.raw_val}")