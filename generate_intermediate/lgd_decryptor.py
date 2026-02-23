"""
generate_intermediate/lgd_decryptor.py
Decrypts the entire LGD file structure into a plaintext binary.
"""

import struct
from logger import logger
from core.context import LgdAnalysisContext
from common.definitions import LgdDefinitions
from common.opcodes import LgdOpcodes

class LgdDecryptor:
    def __init__(self, ctx: LgdAnalysisContext):
        self.ctx = ctx

    def export(self, output_path: str):
        """
        Generates a fully decrypted version of the LGD file.
        """
        if not self.ctx.raw_data:
            logger.error("[LgdDecryptor] No raw data found in context.")
            return

        logger.info(f"[LgdDecryptor] Starting full file decryption...")

        # 1. Create a mutable copy of the original binary
        decrypted_buffer = bytearray(self.ctx.raw_data)
        file_len = len(decrypted_buffer)

        # --- Phase 1: Decrypt P1 Literal Table ---
        # Structure: [Flag (1B)] [Content...] [00] [ID/Size (4B)] [IntVal (4B)]
        # We use entry.str_val length to ensure we STOP exactly before the 00.
        p1_count = 0
        for entry in self.ctx.literal_table:
            if not entry.str_val:
                continue

            # Offset points to Flag. String starts at Offset + 1.
            content_start = entry.offset + 1
            # Use the length of the parsed string (Python string has no null terminator)
            content_len = len(entry.str_val)

            # Validation: Ensure we don't go out of bounds
            if content_start + content_len >= file_len:
                continue

            self._xor_range(
                decrypted_buffer,
                content_start,
                content_len,
                LgdDefinitions.VARIABLE_XOR_KEY # 0x17
            )
            p1_count += 1

        logger.info(f"[LgdDecryptor] Decrypted {p1_count} strings in P1 (Excluding trailing 00).")

        # --- Phase 2: Decrypt P2 Symbol Table ---
        # Structure: [Name...] [00] [FixedBlock (24B)]
        # Offset points to Name start.
        p2_count = 0
        for entry in self.ctx.symbol_table:
            if not entry.name:
                continue

            content_start = entry.offset
            # Use the length of the parsed name
            content_len = len(entry.name)

            if content_start + content_len >= file_len:
                continue

            self._xor_range(
                decrypted_buffer,
                content_start,
                content_len,
                LgdDefinitions.VARIABLE_XOR_KEY # 0x17
            )
            p2_count += 1

        logger.info(f"[LgdDecryptor] Decrypted {p2_count} names in P2 (Excluding trailing 00).")

        # --- Phase 3: Decrypt Bytecode ---
        # Structure: [Size (4B)] [Body (Size Bytes)...]

        # 1. Determine Header Offset
        bc_header_offset = self.ctx.bytecode_offset_start

        # Fallback: If pipeline didn't set it, calculate from Event Table end
        if bc_header_offset == 0:
             if self.ctx.event_tbl_offset_end > 0:
                 bc_header_offset = self.ctx.event_tbl_offset_end
                 logger.warning(f"[LgdDecryptor] Bytecode offset was 0, guessing based on Event Table end: 0x{bc_header_offset:X}")
             else:
                 logger.error("[LgdDecryptor] Cannot locate Bytecode Header (Offsets missing).")
                 return

        # 2. Read Size and Decrypt
        if bc_header_offset + 4 <= file_len:
            # Read Size (Little Endian) from the buffer (Header is NOT encrypted)
            bc_size = struct.unpack('<I', decrypted_buffer[bc_header_offset : bc_header_offset+4])[0]

            # Body starts immediately after Size
            body_start = bc_header_offset + 4
            body_end = body_start + bc_size

            # Clamp to file end if size is weird
            if body_end > file_len:
                logger.warning(f"[LgdDecryptor] Bytecode size {bc_size} exceeds file end. Truncating.")
                body_end = file_len
                bc_size = body_end - body_start

            logger.info(f"[LgdDecryptor] Bytecode found @ 0x{bc_header_offset:X}. Body: 0x{body_start:X} -> 0x{body_end:X} (Size: {bc_size})")

            if bc_size > 0:
                self._xor_range(
                    decrypted_buffer,
                    body_start,
                    bc_size,
                    LgdOpcodes.BYTECODE_XOR_KEY # 0x25
                )
        else:
            logger.error(f"[LgdDecryptor] File too short for Bytecode Header at 0x{bc_header_offset:X}")

        # --- Phase 4: Write Output ---
        try:
            with open(output_path, 'wb') as f:
                f.write(decrypted_buffer)
            logger.info(f"[LgdDecryptor] Success! Saved to: {output_path}")
        except IOError as e:
            logger.error(f"[LgdDecryptor] Failed to write file: {e}")

    def _xor_range(self, buffer: bytearray, start: int, length: int, key: int):
        """Helper to XOR a specific range in the buffer in-place."""
        end = start + length
        # Double check bounds
        if end > len(buffer):
            return

        for i in range(start, end):
            buffer[i] ^= key