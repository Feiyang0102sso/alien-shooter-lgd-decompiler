"""
core/parses.py
"""

import struct
from typing import List, Tuple
from logger import logger
from common.binary_utils import read_xor_string
from common.definitions import LgdDefinitions
from common.structures import P1LiteralEntry, P2SymbolEntry, LgdFileLayout, SpecialEntry, BytecodeEntry
from common.opcodes import LgdOpcodes


class LgdBaseParser:
    def __init__(self, data: bytes):
        self.data = data
        self.length = len(data)


class P1LiteralParser(LgdBaseParser):
    OLD_FLAGS_SET = {0xC1, 0xC2, 0xC5, 0xC6}

    def parse(self, start_offset: int) -> Tuple[List[P1LiteralEntry], int, bool]:
        """
        parse Literal Table
        Returns: (entry_list, next_offset, is_old_version)
        """
        entries = []
        offset = start_offset

        # 1. get Literal Table header info
        if offset + LgdFileLayout.HEADER_SIZE > self.length:
            logger.error_and_stop("Data too short for Literal Table header")
            return [], offset

        count = struct.unpack('<I', self.data[offset:offset + 4])[0]
        offset += 4
        logger.debug(f"[Parser] Reading Literal Table: {count} entries found.")

        # 2. Traversal Reading
        for i in range(count):
            if offset >= self.length: break

            entry_start = offset
            flag = self.data[offset]
            offset += 1

            # Get decrypted string val and corresponding vals
            str_val, offset, s_bytes = read_xor_string(self.data, offset, LgdDefinitions.VARIABLE_XOR_KEY)

            # Get id/size/... (mid 4 bytes)
            raw_id = self.data[offset: offset + 4]
            id_size = struct.unpack(LgdFileLayout.LITERAL_ID_FMT, raw_id)[0]
            offset += 4

            # Get int val last 4 bytes
            raw_int = self.data[offset: offset + 4]
            int_val = struct.unpack(LgdFileLayout.LITERAL_VAL_FMT, raw_int)[0]
            offset += 4

            # Encapsulated
            entry = P1LiteralEntry(
                index=i,
                offset=entry_start,
                next_offset=offset,
                flag=flag,
                str_val=str_val,
                id_size=id_size,
                int_val=int_val,
                raw_flag=flag,
                raw_str=s_bytes,
                raw_id_size=raw_id,
                raw_int_val=raw_int
            )
            entries.append(entry)

        # 3. Version Detection (Old vs New)
        is_old_version = False
        for e in entries:
            if e.flag in self.OLD_FLAGS_SET:
                is_old_version = True
                break

        return entries, offset, is_old_version


class P2SymbolParser(LgdBaseParser):
    def parse(self, start_offset: int) -> Tuple[List[P2SymbolEntry], int]:
        """
        Parse Symbol Table
        Returns: (entry_list, next_offset)
        """
        entries = []
        offset = start_offset

        # 1. Read Symbol Table Header
        if offset + LgdFileLayout.HEADER_SIZE > self.length:
            logger.info("[Parser] End of file reached before Symbol Table.")
            return [], offset

        count = struct.unpack('<I', self.data[offset:offset + 4])[0]
        offset += 4
        logger.debug(f"[Parser] Reading Symbol Table: {count} entries found.")

        # 2. Traversal Reading
        for i in range(count):
            if offset >= self.length:
                break

            entry_start = offset
            # Read Symbol Name
            name, offset, name_bytes = read_xor_string(self.data, offset, LgdDefinitions.VARIABLE_XOR_KEY)

            # fixed 24 bytes
            if offset + LgdFileLayout.SYMBOL_BLOCK_SIZE > self.length:
                logger.warning(f"[Parser] Truncated Symbol Entry at index {i} (Offset: 0x{offset:X})")
                break

            block_data = self.data[offset: offset + LgdFileLayout.SYMBOL_BLOCK_SIZE]
            vals = LgdFileLayout.unpack_symbol_block(block_data)
            offset += LgdFileLayout.SYMBOL_BLOCK_SIZE

            # Encapsulated
            entry = P2SymbolEntry(
                offset=entry_start,
                next_offset=offset,
                name=name,
                raw_name=name_bytes,
                type_val=vals[0],
                garbage=vals[1],
                meta=vals[2],
                p1_idx=vals[3],
                size=vals[4],
                file_id=vals[5],
                run_id=vals[6],
                raw_block=block_data
            )
            entries.append(entry)

        # cal actual_size
        for i in range(len(entries) - 1):
            current_entry = entries[i]
            next_entry = entries[i + 1]

            if next_entry.p1_idx >= current_entry.p1_idx:
                current_entry.actual_size = next_entry.p1_idx - current_entry.p1_idx

        return entries, offset


class FixedTableParser(LgdBaseParser):
    """
    Parses a fixed-size table.
    Reserved for Action and ScriptEvent
    """

    def parse(self, start_offset: int, table_name: str) -> Tuple[List[SpecialEntry], int]:
        entries = []
        offset = start_offset

        total_size = LgdFileLayout.FIXED_TABLE_TOTAL_SIZE
        count = LgdFileLayout.FIXED_TABLE_COUNT
        entry_size = LgdFileLayout.FIXED_ENTRY_SIZE

        if offset + total_size > self.length:
            logger.error_and_stop(f"[Parser] Data too short for {table_name} table.")
            return [], offset

        logger.debug(f"[Parser] Reading {table_name} Table @ 0x{offset:X}")

        raw_block = self.data[offset: offset + total_size]

        for i in range(count):
            # 4 byte per entry
            chunk = raw_block[i * entry_size: (i + 1) * entry_size]

            val = LgdFileLayout.unpack_fixed_entry(chunk)

            if val != 0xFFFFFFFF:
                entry = SpecialEntry(
                    slot_id=i,
                    raw_val=val,
                    target_id=val,
                    offset=offset + (i * entry_size)
                )
                entries.append(entry)
                logger.debug(f"    -> Found {table_name}{i}: points to ID {val}")

        return entries, offset + total_size


class BytecodeParser(LgdBaseParser):
    def parse(self, start_offset: int) -> Tuple[List[BytecodeEntry], int]:
        entries = []
        offset = start_offset

        # 1. Read Total Bytecode Size (Unencrypted 4 bytes)
        if offset + 4 > self.length:
            logger.error_and_stop("[Parser] Data too short for Bytecode Header")
            return [], offset

        bc_size = struct.unpack('<I', self.data[offset:offset + 4])[0]
        logger.debug(f"[Parser] Bytecode Header offset: 0x{offset:X}")
        offset += 4
        logger.debug(f"[Parser] Bytecode starting offset: 0x{offset:X}")
        logger.debug(f"[Parser] Bytecode Block Size: {bc_size} bytes")
        logger.info(f"[Parser] Bytecode Offset Range: 0x{offset:X} -> 0x{offset + bc_size:X}")

        # 2. Read and Decrypt
        end_offset = offset + bc_size
        if end_offset > self.length:
            logger.warning("[Parser] Bytecode size exceeds file length, truncating.")
            end_offset = self.length

        encrypted_data = self.data[offset:end_offset]
        # XOR Decryption
        decrypted_data = bytearray([b ^ LgdOpcodes.BYTECODE_XOR_KEY for b in encrypted_data])

        # 3. Parse Loop
        cursor = 0
        limit = len(decrypted_data)

        # [Debug] Keep track of the last few instructions to identify the crash point
        last_entries = []

        while cursor < limit:
            instr_start = cursor
            current_file_offset = offset + cursor

            # Read Opcode
            opcode = decrypted_data[cursor]
            cursor += 1

            # Look up format
            info = LgdOpcodes.get(opcode)

            mnemonic = info.mnemonic
            operands = []
            fmt = info.format

            # for debug purpose
            # === [Debug] Collapse scene reconstruction ===
            # 1. Gap region check (0x2C - 0x40) -> This is a region that must not exist.
            if LgdOpcodes.MAX_STD_OPCODE < opcode < LgdOpcodes.MIN_EXT_OPCODE:
                logger.error_and_stop("=" * 60)
                logger.error_and_stop(f"[CRASH] Opcode Range Error: Found 0x{opcode:02X} @ 0x{current_file_offset:X}")
                logger.error_and_stop(
                    f"This opcode falls into the INVALID GAP (0x{LgdOpcodes.MAX_STD_OPCODE + 1:02X} - 0x{LgdOpcodes.MIN_EXT_OPCODE - 1:02X})")
                logger.error_and_stop("=" * 60)
                break

            # 2. Extern Call handling (>= 0x41)
            # If the ID is greater than or equal to 65 and less than or equal to 255,
            # it is automatically considered an External Call.
            elif LgdOpcodes.MIN_EXT_OPCODE <= opcode <= LgdOpcodes.MAX_EXT_OPCODE:
                if info.mnemonic.startswith("UNK_"):
                    mnemonic = f"CALL_EXT_{opcode}"
                    # Extern Call does not take bytecode parameters by default
                    # (parameters are on the stack).
                    fmt = None

            # actually no need for this because one single byte can not greater than FF
            # elif opcode > LgdOpcodes.MAX_EXT_OPCODE:

            # --- Operand Parsing ---
            try:
                if fmt == "I":  # 4 bytes unsigned
                    if cursor + 4 <= limit:
                        val = struct.unpack('<I', decrypted_data[cursor:cursor + 4])[0]
                        operands.append(val)
                        cursor += 4

                elif fmt == "i":  # 4 bytes signed
                    if cursor + 4 <= limit:
                        val = struct.unpack('<i', decrypted_data[cursor:cursor + 4])[0]
                        operands.append(val)
                        cursor += 4

                elif fmt == "B":  # 1 byte
                    if cursor + 1 <= limit:
                        val = decrypted_data[cursor]
                        operands.append(val)
                        cursor += 1

                elif fmt == "II":  # 8 bytes (IFF)
                    if cursor + 8 <= limit:
                        val1 = struct.unpack('<I', decrypted_data[cursor:cursor + 4])[0]
                        val2 = struct.unpack('<I', decrypted_data[cursor + 4:cursor + 8])[0]
                        operands.append(val1)
                        operands.append(val2)
                        cursor += 8

                elif fmt == "IB":  # 5 bytes (OP_ASSIGN)
                    if cursor + 5 <= limit:
                        val_id = struct.unpack('<I', decrypted_data[cursor:cursor + 4])[0]
                        val_op = decrypted_data[cursor + 4]
                        operands.append(val_id)
                        operands.append(val_op)
                        cursor += 5

                elif fmt == "S":  # Null-terminated String
                    str_bytes = bytearray()
                    while cursor < limit:
                        char = decrypted_data[cursor]
                        cursor += 1
                        if char == 0x00:
                            break
                        str_bytes.append(char)

                    try:
                        s_val = str_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        s_val = str_bytes.decode('latin-1', errors='replace')
                    operands.append(s_val)

            except Exception as e:
                logger.error(f"[Parser] Error parsing opcode 0x{opcode:02X} at offset 0x{current_file_offset:X}: {e}")
                break

            # Store Entry
            raw = list(decrypted_data[instr_start:cursor])
            entry = BytecodeEntry(
                offset=current_file_offset,
                opcode=opcode,
                # not use info.mnemonic because we dont want to see UNK_XX, replace it as EXT_XX
                mnemonic=mnemonic,
                operands=operands,
                raw_bytes=raw
            )
            # print(entry)
            # logger.debug(entry)
            last_entries.append(entry)
            # print("\n")
            entries.append(entry)
            last_entries.append(entry)


        return entries, end_offset