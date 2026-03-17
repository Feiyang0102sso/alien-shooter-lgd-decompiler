"""
generate_intermediate/renderer_c.py
"""

import struct
from logger import logger
from common.binary_utils import fmt_hex
from common.definitions import LgdDefinitions
from core.context import LgdAnalysisContext


class HumanReadableCRenderer:
    def __init__(self, context: LgdAnalysisContext):
        self.ctx = context

    def render(self, output_path: str):
        lines = []
        lines.extend(self._render_header())
        lines.extend(self._render_part1())
        lines.extend(self._render_part2())

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("\n".join(lines))
            logger.info(f"[C-Renderer] Output written to: {output_path}")
        except Exception as e:
            logger.error_and_stop(f"[C-Renderer] Failed to write file: {e}")

    # --- private function to help in generating ---

    def _reconstruct_script_signature(self, start_idx, total_count):
        params = []
        curr_idx = 0
        para_counter = 1
        while curr_idx < total_count:
            real_idx = start_idx + curr_idx
            if real_idx >= len(self.ctx.literal_table): break
            entry = self.ctx.literal_table[real_idx]
            info = LgdDefinitions.get_flag_info(entry.flag, offset=entry.offset, is_old_version=self.ctx.is_old_version)
            type_name = info['type']
            count = entry.id_size
            if "array" in info['mode'] and count > 1:
                params.append(f"{type_name} para{para_counter}[{count}]")
                curr_idx += count
            else:
                params.append(f"{type_name} para{para_counter}")
                curr_idx += 1
            para_counter += 1
        return ", ".join(params)

    def _reconstruct_extern_signature(self, name, start_idx, total_count):
        params = []
        for i in range(total_count):
            real_idx = start_idx + i
            if real_idx >= len(self.ctx.literal_table): break
            entry = self.ctx.literal_table[real_idx]
            info = LgdDefinitions.get_flag_info(entry.flag, offset=entry.offset, is_old_version=self.ctx.is_old_version)
            type_name = info.get('type', 'int')
            val_str = f'"{entry.str_val}"' if type_name == "string" else str(entry.int_val)
            if type_name == "string" and not entry.str_val: val_str = '""'
            params.append(f"{type_name} para{i + 1} = {val_str}")
        return f"extern {name}({', '.join(params)})"

    def _get_array_content(self, start_idx):
        entry = self.ctx.literal_table[start_idx]
        count = entry.id_size
        info = LgdDefinitions.get_flag_info(entry.flag, offset=entry.offset, is_old_version=self.ctx.is_old_version)
        values = []
        limit = min(start_idx + count, len(self.ctx.literal_table))
        for i in range(start_idx, limit):
            curr = self.ctx.literal_table[i]
            if info.get("type") == "string":
                val = f'"{curr.str_val}"' if curr.str_val else '""'
                values.append(val)
            else:
                values.append(str(curr.int_val))
        return "{" + ", ".join(values) + "}"

    def _get_array_init_string(self, start_idx, count, type_name):
        """
        Read `count` elements starting from `start_idx`
        return the string in the format "{10, 20, 30}".
        """
        values = []
        limit = min(start_idx + count, len(self.ctx.literal_table))

        for i in range(start_idx, limit):
            entry = self.ctx.literal_table[i]
            if type_name == "string":
                # if str array then with ""
                val = f'"{entry.str_val}"' if entry.str_val else '""'
            else:
                # if int array
                val = str(entry.int_val)
            values.append(val)

        return "{ " + ", ".join(values) + " }"

    # --- render algorithm ---

    def _render_header(self):
        return [
            f"// {'=' * 50}",
            f"// LGD ANALYSIS OUTPUT",
            f"// File: {self.ctx.file_path}",
            f"// Size: {self.ctx.file_size} bytes",
            f"// {'=' * 50}\n"
        ]

    def _render_part1(self):
        lines = []
        count = len(self.ctx.literal_table)

        # 1. header info
        lines.append(f"// SECTION 1: LITERAL TABLE (Grouped by GlobalID)")
        lines.append(f"// Range: 0x{self.ctx.p1_offset_start:X} - 0x{self.ctx.p1_offset_end:X}")
        lines.append(f"// Count: {count}")
        lines.append(f"// {'-' * 30}")

        current_global_id = -1

        # track current status
        is_func_context = False
        func_para_counter = 1

        for i, entry in enumerate(self.ctx.literal_table):
            symbol = self.ctx.idx_to_symbol.get(i)

            # get definition info refer in definitions.py
            info = LgdDefinitions.get_flag_info(entry.flag, offset=entry.offset, is_old_version=self.ctx.is_old_version)
            type_name = info['type']
            mode = info.get('mode', 'scalar')  # def_only, array_def, scalar, array_init

            # ---------------------------------------------------------
            # i. Detect GlobalID changes and print the val header.
            # ---------------------------------------------------------
            if entry.global_id != -1 and entry.global_id != current_global_id:
                current_global_id = entry.global_id

                # reset group status
                is_func_context = False
                func_para_counter = 1

                lines.append("")
                lines.append(f"// [GlobalID: {current_global_id}] {'-' * 20}")

                if symbol:
                    t_base = symbol.type_val & 0xFF

                    # A. Function
                    if t_base == LgdDefinitions.BASE_FUNCTION:
                        is_func_context = True
                        sig = self._reconstruct_script_signature(symbol.p1_idx, symbol.size)
                        lines.append(f"// Function: {symbol.name}( {sig} ) {{")
                        lines.append(f"//     (Locals inside this block...)")

                    # B. Extern
                    elif t_base == LgdDefinitions.BASE_EXTERN:
                        lines.append(f"// Extern: {symbol.name} (Extern ID: {symbol.meta})")
                        # lines.append(f"// Extern: {symbol.name}")

                    # C. Variable (included array)
                    else:
                        decl = f"// Variable: {type_name} {symbol.name}"

                        # determine whether initialized
                        is_uninit = mode in ["def_only", "array_def"]

                        # --- for array ---
                        if "array" in mode:
                            decl += f"[{symbol.size}]"  # always show Size
                            if not is_uninit:
                                # Initialized: Generates {val1, val2}
                                init_str = self._get_array_init_string(i, symbol.size, type_name)
                                decl += f" = {init_str};"
                            else:
                                # Uninitialized: direct semicolon
                                decl += ";"

                                # --- scalar ---
                        else:
                            if not is_uninit:
                                # Initialized: Generate = val
                                if type_name == "string":
                                    val_str = f'"{entry.str_val}"' if entry.str_val else '""'
                                    decl += f" = {val_str};"
                                else:
                                    decl += f" = {entry.int_val};"
                            else:
                                # Uninitialized: direct semicolon
                                decl += ";"

                        lines.append(decl)

            # ---------------------------------------------------------
            # ii. Generate Hex data rows
            # ---------------------------------------------------------

            # (1) print comments
            if i in self.ctx.arg_split_map:
                lines.append(f"    {self.ctx.arg_split_map[i]}")

            # (2) build hex string

            # Column 1: Flag + RawString
            hex_part1 = f"{entry.flag:02X} {fmt_hex(entry.raw_str)}"

            # Column 2: String Value, only when it is string
            str_comment = ""
            if type_name == "string" and entry.str_val:
                str_comment = f" /* \"{entry.str_val}\" */"
                str_comment = f"{str_comment:<20}"  #formatting
            else:
                str_comment = " " * 21

            # Column 3: Raw ID/Size
            hex_part2 = f"{fmt_hex(entry.raw_id_size)}"

            # Column 4: ID/Size Comment
            id_comment = ""

            if is_func_context:
                # A: Function parameters -> Force display of Para X
                id_comment = f"/* Para {func_para_counter} */"
                func_para_counter += 1
            else:
                # B: Variables/Arrays

                # check whether it is the first line for the array
                # fixed string[] size fixed at 1
                is_array_head = ("array" in mode) and entry.is_group_head

                if is_array_head:
                    # first line for the array will show the size
                    id_comment = f"/* Size: {entry.id_size} */"

                elif "array" in mode:
                    # array body
                    # always marked as ID
                    if type_name == "string":
                        label = "ID"
                    else:
                        label = "ID"
                    id_comment = f"/* {label}: {entry.id_size} */"

                # foe vars size always be 1
                elif type_name == "string":
                    # normal String val: Size always 1
                    id_comment = f"/* Size: 1 */"

                else:
                    # normal Int val
                    id_comment = f"/* Size: {entry.id_size} */"

            # Column 5: Raw Int Value
            hex_part3 = f"{fmt_hex(entry.raw_int_val)}"

            # Column 6: Int Value Comment
            val_comment = f"/* Val: {entry.int_val} */"

            # append
            # format: Flag+Str | StrVal | IDHex | IDComment | IntHex | ValComment
            final_line = f"    {hex_part1} {str_comment} {hex_part2} {id_comment:<16} {hex_part3} {val_comment}"
            lines.append(final_line)

        lines.append("")
        return lines

    def _render_part2(self):
        lines = []
        count = len(self.ctx.symbol_table)
        lines.append(f"// SECTION 2: SYMBOL TABLE")
        lines.append(f"// Range: 0x{self.ctx.p2_offset_start:X} - 0x{self.ctx.p2_offset_end:X}")
        lines.append(f"// Count: {count}")
        lines.append(f"// {'-' * 30}")

        # Header Bytes
        if len(self.ctx.symbol_table) > 0:
            # Just roughly using the first entry offset minus 4 as start if exists
            pass

        for sym in self.ctx.symbol_table:
            lines.append(f"{fmt_hex(sym.raw_name)} // Name: {sym.name if sym.name else '<root>'}")

            t_base, desc = LgdDefinitions.validate_and_get_desc(sym.type_val, offset=sym.offset)

            logic_desc = ""
            size_label = "Size"

            if t_base == LgdDefinitions.BASE_VARIABLE:
                logic_desc = "Variable"
                size_label = "Declared Variable Length"
            elif t_base == LgdDefinitions.BASE_FUNCTION:
                sig = self._reconstruct_script_signature(sym.p1_idx, sym.size)
                logic_desc = f"Script: {sym.name}({sig})"
                size_label = "Declared Element_Count Para Length"
            elif t_base == LgdDefinitions.BASE_EXTERN:
                logic_desc = self._reconstruct_extern_signature(sym.name, sym.p1_idx, sym.size)
                size_label = "Declared Element_Count Para Length"

            rb = sym.raw_block
            lines.append(f"{fmt_hex(rb[0:2])} // Type: {sym.type_val:04X} ({desc})")
            lines.append(f"{fmt_hex(rb[2:4])} // Garbage: {sym.garbage:04X}")

            meta_cmt = "Meta"
            if t_base == LgdDefinitions.BASE_EXTERN:
                meta_cmt = f"ExternID: {sym.meta}"
            elif t_base == LgdDefinitions.BASE_FUNCTION:
                meta_cmt = f"Offset: {sym.meta}"
            lines.append(f"{fmt_hex(rb[4:8])} // {meta_cmt}")

            lines.append(f"{fmt_hex(rb[8:12])} // P1_Index: {sym.p1_idx}")
            lines.append(f"{fmt_hex(rb[12:16])} // {size_label}: {sym.size}")
            lines.append(f"{fmt_hex(rb[16:20])} // FileID: {sym.file_id}")
            lines.append(f"{fmt_hex(rb[20:24])} // RunID: {sym.run_id}")

            lines.append(f"// Actual Size (P1 Index): {sym.actual_size}")
            lines.append(f"// -> {logic_desc}")
            lines.append("")

        return lines