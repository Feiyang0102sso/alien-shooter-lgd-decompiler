"""
common/opcodes.py
"""
from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class OpcodeInfo:
    code: int
    mnemonic: str
    format: Optional[str] = None
    # Format codes:
    #   None: No operand
    #   "I":  4-byte Unsigned Int (ID, Abs Addr)
    #   "i":  4-byte Signed Int (Rel Offset)
    #   "IB": 4-byte ID + 1-byte SubOp (Special for OP_ASSIGN 0x27)
    #   "II": 8-bytes (IFF special: Offset + Addr)
    #   "S":  Null-terminated String (Variable Length)

    # Behavior Flags (for Analysis/Logging)
    description: str = ""


class LgdOpcodes:
    BYTECODE_XOR_KEY = 0x25

    MAX_STD_OPCODE = 0x2D  # end of common opcodes (CAST_SPR)
    MIN_EXT_OPCODE = 65  # Extern Call begins (0x41)
    MAX_EXT_OPCODE = 255  # Extern Call ends (0xFF)

    _OPCODES = {
        # --- Constants ---
        0x01: OpcodeInfo(0x01, "PUSH_INT", "i", "Push immediate int"),
        0x02: OpcodeInfo(0x02, "PUSH_STR", "S", "Push immediate string"),

        # --- Unary ---
        0x03: OpcodeInfo(0x03, "NEG"),
        0x04: OpcodeInfo(0x04, "BIT_NOT"),
        0x05: OpcodeInfo(0x05, "LOG_NOT"),

        # --- Arithmetic ---
        0x06: OpcodeInfo(0x06, "DIV"),
        0x07: OpcodeInfo(0x07, "MOD"),
        0x08: OpcodeInfo(0x08, "ADD"),
        0x09: OpcodeInfo(0x09, "SUB"),
        0x0A: OpcodeInfo(0x0A, "BIT_XOR"),
        0x0B: OpcodeInfo(0x0B, "BIT_OR"),
        0x0C: OpcodeInfo(0x0C, "BIT_AND"),
        0x13: OpcodeInfo(0x13, "MUL"),
        0x16: OpcodeInfo(0x16, "SHR"),
        0x17: OpcodeInfo(0x17, "SHL"),

        # --- Comparison ---
        0x0D: OpcodeInfo(0x0D, "EQ"),
        0x0F: OpcodeInfo(0x0F, "GT"),
        0x10: OpcodeInfo(0x10, "LT"),
        0x11: OpcodeInfo(0x11, "GE"),
        0x12: OpcodeInfo(0x12, "LE"),
        0x14: OpcodeInfo(0x14, "NE"),

        # --- Logical ---
        0x0E: OpcodeInfo(0x0E, "LOG_OR"),
        0x15: OpcodeInfo(0x15, "LOG_AND"),

        # --- Flow Control ---
        0x18: OpcodeInfo(0x18, "JMP_FALSE", "i", "Jump if false (Offset)"),
        0x19: OpcodeInfo(0x19, "LINE_NUM", "I", "Debug Line Number"),
        0x1A: OpcodeInfo(0x1A, "ARG_COMMIT", None, "Commit arg to stack"),
        #  AWAIT takes 4 bytes (Offset?)
        0x1B: OpcodeInfo(0x1B, "AWAIT", "I", "Async Wait (Offset)"),
        0x1C: OpcodeInfo(0x1C, "JMP", "i", "Unconditional Jump (Offset)"),
        0x1D: OpcodeInfo(0x1D, "IFF", "II", "Special If (SkipOffset + TargetAddr)"),
        0x1E: OpcodeInfo(0x1E, "CALL_FUNC", "I", "Call Function (Global ID)"),
        0x1F: OpcodeInfo(0x1F, "RET"),
        0x2C: OpcodeInfo(0x2C, "AND_JMP", "i", "Short-circuit AND Jump"),
        0x2D: OpcodeInfo(0x2D, "OR_JMP", "i", "Short-circuit OR Jump"),

        # --- Variables ---
        0x20: OpcodeInfo(0x20, "POST_INC", "I", "Post-increment Var ID"),
        0x21: OpcodeInfo(0x21, "POST_DEC", "I"),
        0x22: OpcodeInfo(0x22, "PRE_INC", "I"),
        0x23: OpcodeInfo(0x23, "PRE_DEC", "I"),
        0x24: OpcodeInfo(0x24, "PUSH_VAR", "I", "Push Variable Value (ID)"),
        0x25: OpcodeInfo(0x25, "ADDR_OF", "I", "Get Address of Var (ID)"),

        #  ASSIGN takes an ID
        0x26: OpcodeInfo(0x26, "ASSIGN", "I", "Assign to Var (ID)"),

        # OP_ASSIGN is 5 bytes: ID(4) + SubOp(1)
        0x27: OpcodeInfo(0x27, "OP_ASSIGN", "IB", "Compound Assign (ID + Op)"),

        # ARRAY_IDX is a prefix, no operand itself (consumes stack index)
        0x28: OpcodeInfo(0x28, "ARRAY_IDX", None, "Array Index Prefix"),

        # --- Type Cast ---
        0x29: OpcodeInfo(0x29, "CAST_STR"),
        0x2A: OpcodeInfo(0x2A, "CAST_INT"),
        0x2B: OpcodeInfo(0x2B, "CAST_SPR"),
    }

    # Sub-Op Mapping for 0x27
    ASSIGN_OP_MAP = {
        0x08: "+=", 0x09: "-=", 0x13: "*=", 0x06: "/=",
        0x07: "%=", 0x0C: "&=", 0x0B: "|=", 0x0A: "^=",
        0x16: ">>=", 0x17: "<<="
    }

    @classmethod
    def get(cls, opcode: int) -> OpcodeInfo:
        # Return INFO or a dummy for unknown opcodes to prevent crash
        return cls._OPCODES.get(opcode, OpcodeInfo(opcode, f"UNK_{opcode:02X}"))