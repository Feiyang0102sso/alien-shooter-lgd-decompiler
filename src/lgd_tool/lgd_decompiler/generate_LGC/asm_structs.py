"""
generate_LGC/asm_structs.py
Defines the structure for parsed Assembly Methods and Instructions.
"""
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AsmInstruction:
    offset: int               # ADDR (e.g., 0xC927)
    mnemonic: str             # Opcode (e.g., "PUSH_VAR")
    operands: List[str]       # Operand (e.g., ["upKey_arg0"])

    def __repr__(self):
        # format as: [C927] PUSH_VAR upKey_arg0
        ops_str = " ".join(self.operands)
        return f"[{self.offset:X}] {self.mnemonic} {ops_str}"

class AsmMethod:
    def __init__(self, name: str):
        self.name: str = name
        self.instructions: List[AsmInstruction] = []
        self.addr_map: Dict[int, AsmInstruction] = {} # addr -> instruction for further analyse

    def add_instruction(self, instr: AsmInstruction):
        self.instructions.append(instr)
        self.addr_map[instr.offset] = instr

    def __repr__(self):
        return f"<Method {self.name}: {len(self.instructions)} lines>"