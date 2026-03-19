"""
generate_LGC/cfg_structs.py
Defines the cfg block structure for parsed Method object
"""

from dataclasses import dataclass, field
from typing import List, Any
from lgd_tool.lgd_decompiler.generate_LGC.asm_structs import AsmInstruction


@dataclass
class BasicBlock:
    id: int  # block ID (0, 1, 2...)
    start_offset: int  # starting address
    instructions: List[AsmInstruction] = field(default_factory=list)  # store the instruction

    # [新增]: 存放由 ast_builder 生成的高级语句
    statements: List[Any] = field(default_factory=list)

    # Connections in the graph
    successors: List['BasicBlock'] = field(default_factory=list)  # where do i goto (Out-edges)
    predecessors: List['BasicBlock'] = field(default_factory=list)  # who goto me (In-edges)

    @property
    def end_offset(self) -> int:
        """Address of the last instruction"""
        if not self.instructions:
            return self.start_offset
        return self.instructions[-1].offset

    def __repr__(self):
        pre_ids: List[str] = [str(b.id) for b in self.predecessors]
        succ_ids = [str(b.id) for b in self.successors]
        return (f"<{pre_ids} -> "
                f"Block {self.id} @ {self.start_offset:X} "
                f"({len(self.instructions)} instrs) "
                f"-> {succ_ids}>")