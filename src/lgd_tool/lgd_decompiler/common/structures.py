"""
common/structures.py
structure for lgd files and output files
"""

import struct
from dataclasses import dataclass
from typing import List


@dataclass
class P1LiteralEntry:
    """
    corresponding to an entry in  Literal Table (P1)
    contains int vals and str values, and the Global ID
    """
    index: int  # array index
    offset: int  # current entry offset
    next_offset: int  # current entry end

    # val after parse
    flag: int # 1 byte
    str_val: str  # str val after decrypt 0x17 n bytes, end with 00
    id_size: int  # array size or its id, 4 bytes, always 1 for non-array variables
    int_val: int  # int val 4 bytes signed


    # original bytes, in hex dump format
    raw_flag: int
    raw_str: List[int]
    raw_id_size: bytes
    raw_int_val: bytes

    # add for global ID
    global_id: int = -1
    # mark is it the first line of the group/Array
    is_group_head: bool = False


@dataclass
class P2SymbolEntry:
    """
    corresponding to an entry in  Symbol Table (P2)
    contains variable / function names, types, p1_index, file id ...
    """
    offset: int
    next_offset: int

    # val after parse
    name: str  # variable name

    # val in 24 bytes blocks
    type_val: int  # type 2 bytes
    garbage: int  # unknown 2 bytes
    meta: int  #  ExternID / Offset / Meta /unknown/ 4 bytes
    p1_idx: int  # index pointer to Literal Table 4 bytes
    size: int  # updated: Array length or Param count ( Element_Count ) actually
    file_id: int  # file ID (from which #included files) not accurate for functions
    run_id: int  # Runtime ID ? not for sure

    # original
    raw_name: List[int]
    raw_block: bytes  # fixed 24 bytes block

    # The actual size p1_index used (obtained by calculating the p1_idx of the next Symbol).
    actual_size: int = 0

@dataclass
class SpecialEntry:
    """
    Represents an entry in the fixed Action or ScriptEvent tables.
    Each table has 256 slots.
    """
    slot_id: int  # 0-255 (The X in ActionX / ScriptEventX)
    raw_val: int  # The 4-byte integer read from file
    target_id: int  # The parsed ID (P1 Index or Global ID, depending on logic)
    offset: int  # File offset

    @property
    def is_defined(self) -> bool:
        # 0xFFFFFFFF (-1) means undefined/empty
        return self.raw_val != 0xFFFFFFFF

class LgdFileLayout:
    """lgd physical layouts"""
    HEADER_SIZE = 4  # header for each section is fixed (uint32)

    # Literal Table (P1) don't have fix  Struct, Flag+Str+UInt32+Int32
    LITERAL_ID_FMT = '<I'  # uint32
    LITERAL_VAL_FMT = '<i'  # int32

    # Symbol Table (P2) Block fixed 24
    SYMBOL_BLOCK_SIZE = 24
    # format: Type(2), Garbage(2), Meta(4), P1Idx(4), Size(4), FileID(4), RunID(4)
    SYMBOL_BLOCK_FMT = '<HHIIIII'

    # special table
    FIXED_TABLE_COUNT = 256
    FIXED_ENTRY_SIZE = 4
    FIXED_ENTRY_FMT = '<I'  # unsigned int (0xFFFFFFFF = undefined)
    FIXED_TABLE_TOTAL_SIZE = FIXED_TABLE_COUNT * FIXED_ENTRY_SIZE

    @staticmethod
    def unpack_symbol_block(data: bytes):
        return struct.unpack(LgdFileLayout.SYMBOL_BLOCK_FMT, data)

    @staticmethod
    def unpack_fixed_entry(data: bytes):
        """Helper to unpack a single fixed table entry"""
        return struct.unpack(LgdFileLayout.FIXED_ENTRY_FMT, data)[0]


@dataclass
class BytecodeEntry:
    """
    Represents a single parsed instruction in the Bytecode section.
    """
    offset: int  # File offset where this opcode starts
    opcode: int  # The opcode value (e.g., 0x01)
    mnemonic: str  # Human-readable name (e.g., "PUSH_INT")

    # Operands: Can contain ints or strings
    # For "I": [int_val]
    # For "S": ["StringValue"]
    operands: List[any]

    # Raw bytes for hex dump (opcode + operands)
    raw_bytes: List[int]

    def __str__(self):
        # Helper for simple print
        ops_str = ""
        if self.operands:
            formatted_ops = []
            for op in self.operands:
                if isinstance(op, str):
                    formatted_ops.append(f'"{op}"')
                elif isinstance(op, int):
                    # [修复] 启发式双轨显示: 解决大掩码(0x80000004)变成无意义大负数, 小逻辑负数(-999999, -1)变成无意义大正十六进制的问题
                    if 0 <= op <= 0xFFFF:
                        # 1. 常规小正数(0~65535)，保留最直观的十进制显示
                        val = str(op)
                    elif -9999999 <= op < 0:
                        # 2. 常规逻辑负数(如 -1, -10000, -999999)，直接展示十进制负数
                        val = str(op)
                    else:
                        # 3. 超出常规范围(极大的正负数, 如 0x80000004 被算作 -2147483644)，极大概率是位掩码或内存常量。统一以 32位无符号 HEX 展现
                        u_op = op & 0xFFFFFFFF
                        val = f"0x{u_op:X}"
                    formatted_ops.append(val)
                else:
                    formatted_ops.append(str(op))
            ops_str = ", ".join(formatted_ops)

        return f"[0x{self.offset:X}] {self.mnemonic:<12} {ops_str}"