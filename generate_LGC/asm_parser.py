"""
generate_LGC/asm_parser.py
Parses the generated ASM text file into structured AsmMethod objects.
"""
import re
from typing import List, Optional
from logger import logger

from generate_LGC.asm_structs import AsmMethod, AsmInstruction



class AsmParser:
    # RE
    RE_BEGIN = re.compile(r"^;Function\s+(\w+)\(\)\s+Begin", re.IGNORECASE)
    RE_END = re.compile(r"^;Function\s+(\w+)\(\)\s+End", re.IGNORECASE)

    # Group 1: Hex Addr
    # Group 2: Mnemonic
    # Group 3: Operands + Comments
    RE_INSTR = re.compile(r"^\s*([0-9A-Fa-f]+):\s+(?:(?:[0-9A-Fa-f]{2}\s?)+)\s+(\w+)(?:\s+(.*))?")

    def parse_file(self, file_path: str) -> List[AsmMethod]:
        methods = []
        current_method: Optional[AsmMethod] = None
        current_start_line: int = 0

        # summarize vars
        stats_total = 0
        stats_success = 0
        stats_fail = 0
        error_func_name = []

        logger.info(f"[ASM-PARSER] Starting ASM parse: {file_path}")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            logger.error(f"[ASM-PARSER] File not found: {file_path}")
            return []

        for i, line in enumerate(lines):
            line_num = i # + 1  # it seems no need to plus 1 actually
            line = line.strip()

            if not line:
                continue

            # --- 1. Func Begin ---
            match_begin = self.RE_BEGIN.match(line)
            if match_begin:
                # If the previous one wasn't closed, report an error first.
                if current_method:
                    logger.error(
                        f"[ASM-PARSER] [Line {line_num}] Nested Begin detected! Previous method '{current_method.name}' (started at line {current_start_line}) was not closed.")
                    stats_fail += 1
                    # Force it to be closed
                    methods.append(current_method)

                name = match_begin.group(1)
                current_method = AsmMethod(name)
                current_start_line = line_num
                stats_total += 1
                continue

            # --- 2. Func End ---
            match_end = self.RE_END.match(line)
            if match_end:
                end_name = match_end.group(1)

                if not current_method:
                    logger.error(f"[ASM-PARSER] [Line {line_num}] Orphan 'End' tag found for '{end_name}' without matching 'Begin'.")
                    continue

                # check
                has_error = False


                # check A: name check
                if current_method.name != end_name:
                    logger.error(
                        f"[ASM-PARSER] [Line {line_num}] Method Name Mismatch! Begin: '{current_method.name}', End: '{end_name}'.")
                    has_error = True

                # check B: Must End with RET
                if not current_method.instructions:
                    logger.error(f"[ASM-PARSER] [Line {line_num}] Method '{current_method.name}' is empty.")
                    has_error = True
                else:
                    last_instr = current_method.instructions[-1]
                    if last_instr.mnemonic != 'RET':
                        logger.error(
                            f"[ASM-PARSER] [Line {line_num}] Method '{current_method.name}' does not end with RET. Last instruction: {last_instr.mnemonic} at Addr {last_instr.offset:X}.")
                        has_error = True

                # summarize
                if has_error:
                    stats_fail += 1
                    error_func_name.append(current_method.name)
                else:
                    stats_success += 1
                    # logger.debug(
                    #     f"[ASM-PARSER] Parsed Method '{current_method.name}': {len(current_method.instructions)} instructions.")

                methods.append(current_method)
                current_method = None
                continue

            # --- 3. in function parses ---
            if current_method:
                match_instr = self.RE_INSTR.match(line)
                if match_instr:
                    try:
                        offset = int(match_instr.group(1), 16)
                        mnemonic = match_instr.group(2)
                        raw_args = match_instr.group(3) or ""

                        # operands = raw_args.split(';')[0].strip().split()
                        # operands = [op for op in operands if op]

                        clean_args_str = raw_args.split(';')[0].replace(',', ' ').strip()
                        operands = clean_args_str.split()

                        instr = AsmInstruction(offset, mnemonic, operands)
                        current_method.add_instruction(instr)
                    except Exception as e:
                        logger.error(
                            f"[ASM-PARSER] [Line {line_num}] Instruction parse error in '{current_method.name}': {e} | Content: {line}")
                # else:
                #   ignore the second line if it is too long e.g. IFF / PUSH_STR
                pass

        # --- 4. check when file ended but function not end  ---
        if current_method:
            logger.error(
                f"[ASM-PARSER] File ended but method '{current_method.name}' (started at line {current_start_line}) was not closed.")
            stats_fail += 1
            methods.append(current_method)

        # --- 5. summarize  ---
        logger.info("-" * 40)
        logger.info(f"[ASM-PARSER] Parsing Summary: Total: {stats_total} | Success: {stats_success} | Failed: {stats_fail}")
        if stats_fail > 0:
            logger.error(f"[ASM-PARSER] Fail Function names: {', '.join(error_func_name)}")
        logger.info("-" * 40)

        return methods