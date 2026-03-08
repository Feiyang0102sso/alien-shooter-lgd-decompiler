"""
generate_intermediate/exporter_csv.py
Export analysis data to CSV for machine consumption (Decompiler/Tools).
One row per Variable/Symbol definition (including Local Variables).
"""

import csv
import json
from typing import List, Dict, Any, Optional
from logger import logger
from common.definitions import LgdDefinitions
from common.structures import P1LiteralEntry, P2SymbolEntry
from core.context import LgdAnalysisContext


class LgdCsvExporter:
    def __init__(self, context: LgdAnalysisContext):
        self.ctx = context
        # Define CSV Headers
        self.headers = [
            "Global_ID",
            "P1_Index",
            "File_ID",      # [New] From P2 Symbol (Source file ID)
            "Name",
            "Category",     # VAR, FUNC, EXTERN, LOCAL_VAR
            "Type",         # int, string, N/A (for FUNC/EXTERN)
            "Is_Array",     # True/False
            "Size",         # Array Length or Param Count
            "Is_Initialized", # True/False
            "Init_Value",   # Scalar value or JSON Array String
            "Extern_ID",    # ID for extern functions
            "Param_Types"   # string joined by ';' e.g. "int;string"
        ]

    def export(self, output_path: str):
        """
        Main export function to write the CSV file.
        """
        # 1. Group existing P1 data by Global ID
        grouped_data = self._group_by_global_id()

        # 2. Reconstruct the Symbol order to ensure we catch symbols with NO P1 entries (Size 0)
        # This logic must match Analyzer._analyze_global_ids strictly
        valid_symbols = [s for s in self.ctx.symbol_table if s.p1_idx <= len(self.ctx.literal_table)]
        sorted_symbols = sorted(valid_symbols, key=lambda s: s.p1_idx)

        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=self.headers)
                writer.writeheader()

                # Iterate through logical Global IDs (0, 1, 2...) matching the Symbol List
                for gid, symbol in enumerate(sorted_symbols):
                    # Get P1 entries if they exist (Variables, Non-empty Funcs)
                    entries = grouped_data.get(gid, [])

                    # Process even if entries is empty (e.g. Size 0 Extern)
                    rows = self._process_group(gid, entries, symbol)

                    if rows:
                        writer.writerows(rows)

            logger.info(f"[Exporter] CSV exported to: {output_path}")

        except Exception as e:
            logger.error_and_stop(f"[Exporter] Failed to write CSV: {e}")
            import traceback
            traceback.print_exc()

    def _group_by_global_id(self) -> Dict[int, List[P1LiteralEntry]]:
        """
        Helper: Group flat literal table entries by their Global ID.
        Returns: { global_id: [entry1, entry2, ...] }
        """
        groups = {}
        for entry in self.ctx.literal_table:
            # Skip entries that haven't been assigned a Global ID
            if entry.global_id == -1:
                continue

            if entry.global_id not in groups:
                groups[entry.global_id] = []
            groups[entry.global_id].append(entry)
        return groups

    def _process_group(self, gid: int, entries: List[P1LiteralEntry], symbol: Optional[P2SymbolEntry]) -> List[Dict[str, Any]]:
        """
        Convert a group of entries (and/or a Symbol) into CSV rows.
        """
        # If we have neither entries nor a symbol, this ID is invalid
        if not entries and not symbol:
            return []

        rows_to_return = []

        # Head is the first P1 entry, if available
        head = entries[0] if entries else None

        # --- 1. Extract Common Metadata ---

        # File ID comes from P2 Symbol.
        file_id = symbol.file_id if symbol else "N/A"

        # Name defaults to UNK_{GID} if symbol is missing
        if not symbol or not symbol.name:
            err_msg = f"[Exporter] Missing symbol name for Global ID {gid}. Using fallback."
            logger.error_and_stop(err_msg)
        
        symbol_name = symbol.name if symbol else f"UNK_{gid}"

        # P1 Index: Use Head's index or Symbol's P1 pointer
        p1_index = head.index if head else (symbol.p1_idx if symbol else -1)

        # Determine Main Category
        category = "VAR"
        if symbol:
            t_base = symbol.type_val & 0xFF
            if t_base == LgdDefinitions.BASE_FUNCTION:
                category = "FUNC"
            elif t_base == LgdDefinitions.BASE_EXTERN:
                category = "EXTERN"

        # --- 2. Generate The "Header" Row (The Function/Global itself) ---
        main_row: Dict[str, Any] = {h: "N/A" for h in self.headers}
        main_row["Global_ID"] = gid
        main_row["P1_Index"] = p1_index
        main_row["File_ID"] = file_id
        main_row["Name"] = symbol_name
        main_row["Category"] = category

        # Fill details specific to the category for the main row
        self._fill_main_row_details(main_row, category, head, symbol, entries)
        rows_to_return.append(main_row)

        # --- 3. Generate Local Variable Rows (Only for FUNC with P1 entries) ---
        if category == "FUNC" and entries:
            # For functions, Symbol Size represents the Parameter slots.
            param_slots = symbol.size if symbol else 0
            i = 0
            param_idx = 0

            # Use while loop to correctly skip array element entries
            while i < len(entries):
                entry = entries[i]
                info = LgdDefinitions.get_flag_info(entry.flag)
                mode = info.get('mode', 'scalar')
                data_type = info['type']
                is_array = "array" in mode

                # Parse Initialization status based on mode
                is_uninit = mode in ["def_only", "array_def"]

                # Determine if it's a Parameter or Local Variable based on slot limit
                if i < param_slots:
                    cat = "PARAM"
                    name = f"{symbol_name}_arg{param_idx}"
                    param_idx += 1
                else:
                    cat = "LOCAL_VAR"
                    # Calculate relative offset to align with engine's bytecode addressing
                    local_offset = i - param_slots
                    name = f"{symbol_name}@local{local_offset}"

                    # Add warning for uninitialized non-static local arrays
                    if is_array and is_uninit:
                        logger.warning(
                            f"[CSV EXPORTER] Found uninitialized local array in {symbol_name}: "
                            f"{name} (Size: {entry.id_size}, P1_Index: {entry.index}). "
                            f"Check if the engine assigns values properly!"
                        )

                sub_row: Dict[str, Any] = {h: "N/A" for h in self.headers}
                sub_row["Global_ID"] = gid
                sub_row["P1_Index"] = entry.index
                sub_row["File_ID"] = file_id
                sub_row["Name"] = name
                sub_row["Category"] = cat
                sub_row["Type"] = data_type
                sub_row["Is_Array"] = "True" if is_array else "False"
                sub_row["Size"] = entry.id_size
                sub_row["Is_Initialized"] = "False" if is_uninit else "True"

                # Extract Init_Value dynamically like global variables
                if not is_uninit:
                    if is_array:
                        vals = []
                        # Fetch all elements within the array bounds
                        for e in entries[i: i + entry.id_size]:
                            val = e.str_val if data_type == "string" else e.int_val
                            if data_type == "string" and val is None: val = ""
                            vals.append(val)
                        sub_row["Init_Value"] = json.dumps(vals)
                    else:
                        val = entry.str_val if data_type == "string" else entry.int_val
                        if data_type == "string" and val is None: val = ""
                        sub_row["Init_Value"] = str(val)

                rows_to_return.append(sub_row)

                # Advance index by array size to avoid treating array elements as new variables
                step = entry.id_size if (is_array and entry.id_size > 1) else 1
                i += step

        return rows_to_return

    def _fill_main_row_details(self, row, category, head: Optional[P1LiteralEntry], symbol: Optional[P2SymbolEntry], entries: List[P1LiteralEntry]):
        """
        Helper to fill Type, Init_Value, Size, and Param_Types
        """
        # Get Mode/Type info from P1 Head if available
        if head:
            info = LgdDefinitions.get_flag_info(head.flag)
            mode = info.get('mode', 'scalar')
            data_type = info['type']
        else:
            # Fallback if no P1 data (e.g. Size 0 Extern)
            mode = 'scalar'
            data_type = 'N/A'

        # Symbol size is authoritative
        size = symbol.size if symbol else (head.id_size if head else 0)
        row["Size"] = size

        if category == "VAR":
            row["Type"] = data_type
            row["Is_Array"] = "True" if "array" in mode else "False"

            # Variables strictly require P1 entries to determine value
            if head:
                is_uninit = mode in ["def_only", "array_def"]
                row["Is_Initialized"] = "False" if is_uninit else "True"

                if not is_uninit:
                    if "array" in mode:
                        vals = []
                        for e in entries[:size]:
                            val = e.str_val if data_type == "string" else e.int_val
                            if data_type == "string" and val is None: val = ""
                            vals.append(val)
                        row["Init_Value"] = json.dumps(vals)
                    else:
                        val = head.str_val if data_type == "string" else head.int_val
                        if data_type == "string" and val is None: val = ""
                        row["Init_Value"] = str(val)

        elif category == "FUNC":
            row["Type"] = "N/A"
            row["Is_Array"] = "False"

            # Construct Param Types if entries exist
            if size > 0 and entries:
                p_types = []
                for i in range(min(size, len(entries))):
                    p_info = LgdDefinitions.get_flag_info(entries[i].flag)
                    p_types.append(p_info['type'])
                row["Param_Types"] = ";".join(p_types)
            else:
                row["Param_Types"] = "N/A"

        elif category == "EXTERN":
            row["Type"] = "N/A"
            row["Is_Array"] = "False"
            row["Extern_ID"] = symbol.meta if symbol else "N/A"

            # Construct Param Types if entries exist
            if size > 0 and entries:
                p_types = []
                for i in range(min(size, len(entries))):
                    p_info = LgdDefinitions.get_flag_info(entries[i].flag)
                    p_types.append(p_info['type'])
                row["Param_Types"] = ";".join(p_types)
            else:
                row["Param_Types"] = "N/A"