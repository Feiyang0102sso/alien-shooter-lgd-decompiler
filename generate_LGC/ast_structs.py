"""
generate_LGC/ast_structs.py
Defines the Abstract Syntax Tree (AST) nodes for expression recovery.
"""
from dataclasses import dataclass
from typing import List, Optional, Union


# ==========================================
# Base Node
# ==========================================
class ASTNode:
    def to_code(self) -> str:
        """递归生成伪代码的方法"""
        raise NotImplementedError


# ==========================================
# Expressions (表达式：产生值的节点，存在于栈中)
# ==========================================
@dataclass
class ConstNode(ASTNode):
    value: Union[int, str]
    type_name: str  # 'int' or 'str'

    def to_code(self) -> str:
        if self.type_name == 'str':
            return f'"{self.value}"'
        # 针对 int，可以根据需要格式化为 hex
        if isinstance(self.value, int) and self.value > 9:
            return f"0x{self.value:X}"
        else:
            return str(self.value)


@dataclass
class VarNode(ASTNode):
    name: str

    def to_code(self) -> str:
        return self.name


@dataclass
class UnaryOpNode(ASTNode):
    op: str  # e.g., '-', '!', '~', '&', '++', '--'
    operand: ASTNode
    is_postfix: bool = False  # 区分 ++i 和 i++

    def to_code(self) -> str:
        if self.is_postfix:
            return f"({self.operand.to_code()}{self.op})"
        return f"({self.op}{self.operand.to_code()})"


@dataclass
class BinaryOpNode(ASTNode):
    op: str  # e.g., '+', '>=', '&&'
    left: ASTNode
    right: ASTNode

    def to_code(self) -> str:
        return f"({self.left.to_code()} {self.op} {self.right.to_code()})"


@dataclass
class CallExprNode(ASTNode):
    """函数调用也可以作为表达式存在栈中（有返回值）"""
    func_name: str
    args: List[ASTNode]

    def to_code(self) -> str:
        args_str = ", ".join(arg.to_code() for arg in self.args)
        return f"{self.func_name}({args_str})"


@dataclass
class ArrayAccessNode(ASTNode):
    array: ASTNode
    index: ASTNode

    def to_code(self) -> str:
        return f"{self.array.to_code()}[{self.index.to_code()}]"


@dataclass
class CastNode(ASTNode):
    target_type: str
    operand: ASTNode

    def to_code(self) -> str:
        return f"({self.target_type}){self.operand.to_code()}"


# ==========================================
# Statements (语句：完整的动作，存在于 Block 的 statements 列表中)
# ==========================================
@dataclass
class AssignNode(ASTNode):
    target: str
    value: ASTNode
    op: str = "="
    def to_code(self) -> str:
        # 注意！这里只有纯粹的表达式，没有末尾的 ';'
        return f"{self.target} {self.op} {self.value.to_code()}"


@dataclass
class ExprStmtNode(ASTNode):
    """用于将任何表达式（如函数调用、i++）包装成一个独立的语句"""
    expr: ASTNode
    def to_code(self) -> str:
        return f"{self.expr.to_code()};"

@dataclass
class CallStmtNode(ASTNode):
    """当函数调用不作为右值，而是独立成句时"""
    call_expr: CallExprNode

    def to_code(self) -> str:
        return f"{self.call_expr.to_code()};"


@dataclass
class ReturnNode(ASTNode):
    value: Optional[ASTNode] = None

    def to_code(self) -> str:
        if self.value:
            return f"return {self.value.to_code()};"
        return "return;"


@dataclass
class JumpNode(ASTNode):
    condition: Optional[ASTNode]
    target_addr: int
    jump_type: str  # 'JMP', 'JMP_FALSE', 'AND_JMP' 等

    def to_code(self) -> str:
        if self.condition:
            return f"if ({self.jump_type}: {self.condition.to_code()}) goto loc_{self.target_addr:X};"
        return f"goto loc_{self.target_addr:X};"


@dataclass
class AwaitNode(ASTNode):
    target_addr: int

    def to_code(self) -> str:
        return f"await(loc_{self.target_addr:X});"


@dataclass
class LineNumNode(ASTNode):
    line_num: int

    def to_code(self) -> str:
        return f"// --- Line {self.line_num} ---"

@dataclass
class CommentNode(ASTNode):
    text: str
    def to_code(self) -> str:
        return f"// {self.text}"