"""
src/lgd_tool/crypt/cryptor.py
LgdCryptor class for encrypting and decrypting LGD binary files.
"""

import struct
from pathlib import Path

# ==============================================================================
# Constants Config
# ==============================================================================
VARIABLE_XOR_KEY = 0x17
BYTECODE_XOR_KEY = 0x25
FIXED_TABLES_SIZE = 2048  # Action table (1024) + ScriptEvent table (1024)


class LgdCryptor:
    """
    LgdCryptor is responsible for processing LGD binary data.
    It scans the file structures and applies symmetrical XOR processing 
    on Literal string values, Symbol name values, and the Bytecode body.
    """

    def __init__(self):
        """
        Initializes the LgdCryptor instance.
        """
        pass

    def transform(self, data: bytes) -> bytes:
        """
        Processes LGD binary data. It performs structural scanning and
        toggles the encryption state (encrypts if decrypted, decrypts if encrypted).

        :param data: The input LGD file content bytes.
        :return: The transformed LGD file content bytes.
        """
        file_len = len(data)
        if file_len < 4:
            # Data too short, return as-is
            return data

        offset = 0

        # --- Step 1: Parse P1 Literal Table ---
        p1_count = struct.unpack('<I', data[offset : offset + 4])[0]
        offset = offset + 4

        p1_ranges = []
        for _ in range(p1_count):
            if offset >= file_len:
                break

            # Flag is 1 byte, string starts right after it
            str_start = offset + 1
            str_len, next_offset = self._find_string_bounds(data, str_start)
            p1_ranges.append((str_start, str_len))

            # Skip id_size (4 bytes) + int_val (4 bytes)
            offset = next_offset + 8

        # --- Step 2: Parse P2 Symbol Table ---
        if offset + 4 > file_len:
            # Reached end of file early
            return self._apply_xor(data, p1_ranges, [], (0, 0))

        p2_count = struct.unpack('<I', data[offset : offset + 4])[0]
        offset = offset + 4

        p2_ranges = []
        for _ in range(p2_count):
            if offset >= file_len:
                break

            name_start = offset
            name_len, next_offset = self._find_string_bounds(data, name_start)
            p2_ranges.append((name_start, name_len))

            # Skip 24 bytes fixed symbol block data
            offset = next_offset + 24

        # --- Step 3: Skip Action Table and ScriptEvent Table ---
        offset = offset + FIXED_TABLES_SIZE

        # --- Step 4: Parse Bytecode ---
        bytecode_range = (0, 0)
        if offset + 4 <= file_len:
            bc_size = struct.unpack('<I', data[offset : offset + 4])[0]
            body_start = offset + 4

            # Clamp logic to prevent out of bounds
            if body_start + bc_size > file_len:
                bc_size = file_len - body_start

            bytecode_range = (body_start, bc_size)

        # --- Step 5: Apply XOR Transformations ---
        transformed_data = self._apply_xor(data, p1_ranges, p2_ranges, bytecode_range)
        return transformed_data

    def _find_string_bounds(self, data: bytes, start: int) -> tuple[int, int]:
        """
        Locates the null terminator (0x00) of a string starting from 'start'.

        :param data: The binary data to scan.
        :param start: Starting index of the string.
        :return: A tuple of (string_byte_length, offset_after_null_terminator).
        """
        curr = start
        limit = len(data)
        while curr < limit:
            if data[curr] == 0x00:
                break
            curr = curr + 1

        length = curr - start
        next_offset = curr + 1
        return length, next_offset

    def _apply_xor(self, data: bytes, p1_ranges: list, p2_ranges: list, bytecode_range: tuple) -> bytes:
        """
        Applies XOR transformations using keys on the collected index ranges.

        :param data: Original binary bytes.
        :param p1_ranges: List of (start, len) tuples for P1 Literal strings.
        :param p2_ranges: List of (start, len) tuples for P2 Symbol names.
        :param bytecode_range: A tuple of (start, len) for Bytecode body.
        :return: Transformed bytes.
        """
        buffer = bytearray(data)
        file_len = len(buffer)

        # Apply XOR on P1 Literal strings
        for start, length in p1_ranges:
            end = start + length
            if end <= file_len:
                for i in range(start, end):
                    buffer[i] = buffer[i] ^ VARIABLE_XOR_KEY

        # Apply XOR on P2 Symbol names
        for start, length in p2_ranges:
            end = start + length
            if end <= file_len:
                for i in range(start, end):
                    buffer[i] = buffer[i] ^ VARIABLE_XOR_KEY

        # Apply XOR on Bytecode body
        bc_start, bc_len = bytecode_range
        if bc_len > 0:
            bc_end = bc_start + bc_len
            if bc_end <= file_len:
                for i in range(bc_start, bc_end):
                    buffer[i] = buffer[i] ^ BYTECODE_XOR_KEY

        return bytes(buffer)
