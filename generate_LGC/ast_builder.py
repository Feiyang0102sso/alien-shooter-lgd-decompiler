"""
generate_LGC/ast_builder.py
Translates linear assembly instructions into AST structures using symbolic execution.
Optimized for high-level expression recovery and cross-block stack consistency.
"""
import re
from typing import Dict, Tuple
from logger import logger

from generate_LGC.cfg_structs import BasicBlock
from generate_LGC.ast_structs import *

class ASTBuilder:
    def __init__(self, ext_def_map: Optional[Dict[int, Tuple[str, int]]] = None,
                       func_def_map: Optional[Dict[int, str]] = None):
        self.EXT_DEF_MAP = ext_def_map or {}
        self.FUNC_DEF_MAP = func_def_map or {}

        self.current_offset = 0
        self.current_mnemonic = ""
        self.current_method_name = "Unknown"

        self.BIN_OP_MAP = {
            'ADD': '+', 'SUB': '-', 'MUL': '*', 'DIV': '/', 'MOD': '%',
            'BIT_AND': '&', 'BIT_OR': '|', 'BIT_XOR': '^',
            'SHL': '<<', 'SHR': '>>',
            'EQ': '==', 'NE': '!=', 'GT': '>', 'LT': '<', 'GE': '>=', 'LE': '<=',
            'LOG_AND': '&&', 'LOG_OR': '||'
        }
        self.UNARY_OP_MAP = {
            'NEG': '-', 'BIT_NOT': '~', 'LOG_NOT': '!'
        }

    def _safe_pop(self, stack: List[ASTNode]) -> ASTNode:
        if stack:
            return stack.pop()

        logger.error_and_stop(f"[AST-BUILDER] Stack_In Triggered in '{self.current_method_name}'! Underflow at Addr: 0x{self.current_offset:X} | Instr: {self.current_mnemonic}")
        return VarNode("Stack_In")

    def build_block_ast(self, block: BasicBlock, is_last_physical_block: bool = False, method_name: str = "Unknown") -> List[ASTNode]:
        self.current_method_name = method_name
        stack: List[ASTNode] = []
        statements: List[ASTNode] = []

        pending_func_args: Dict[str, Dict[int, ASTNode]] = {}
        pending_args_fallback: List[ASTNode] = []

        # pending_args: List[ASTNode] = []
        pending_array_index: Optional[ASTNode] = None

        for i, instr in enumerate(block.instructions):
            self.current_offset = instr.offset
            self.current_mnemonic = instr.mnemonic
            mne = instr.mnemonic
            ops = instr.operands

            try:
                # --- 1. Push Operations ---
                if mne == 'PUSH_INT':
                    val_str = ops[0].strip()
                    val = -int(val_str[3:], 16) if val_str.startswith('0x-') else int(val_str, 0)
                    stack.append(ConstNode(val, 'int'))
                elif mne == 'PUSH_STR':
                    val = " ".join(ops) if ops else ""
                    if val.startswith('"') and val.endswith('"'):
                        val = val[1:-1]

                    # to make each \ become \\ otherwise the game would crash
                    val = val.replace('\\', '\\\\').replace('"', '\\"')
                    stack.append(ConstNode(val, 'str'))

                elif mne == 'PUSH_VAR':
                    var_name = ops[0]

                    # ==========================================
                    # [终极去噪] 跨域默认参数探测器
                    # 匹配格式: FunctionName_argX 或 FunctionName_localX
                    # ==========================================
                    match = re.match(r'^([a-zA-Z0-9_]+)_(arg|local)\d+$', var_name)
                    if match and match.group(1) != self.current_method_name:
                        # 打上废弃标记，稍后组装函数时直接删掉！
                        dummy_node = VarNode("__DUMMY_ARG__")
                        if pending_array_index is not None:
                            stack.append(ArrayAccessNode(dummy_node, pending_array_index))
                            pending_array_index = None
                        else:
                            stack.append(dummy_node)
                    else:
                        if pending_array_index is not None:
                            stack.append(ArrayAccessNode(VarNode(var_name), pending_array_index))
                            pending_array_index = None
                        else:
                            stack.append(VarNode(var_name))

                elif mne == 'ADDR_OF':
                    stack.append(UnaryOpNode('&', VarNode(ops[0])))

                # --- 2. Assignments ---
                elif mne == 'ASSIGN' or mne == 'OP_ASSIGN':
                    target_var = ops[0]
                    op = ops[1] if mne == 'OP_ASSIGN' else "="
                    value = self._safe_pop(stack)

                    if pending_array_index is not None:
                        target_var = f"{target_var}[{pending_array_index.to_code()}]"
                        pending_array_index = None

                    assign_expr = AssignNode(target_var, value, op=op)
                    stack.append(assign_expr)

                elif mne == 'ARRAY_IDX':
                    pending_array_index = self._safe_pop(stack)

                # --- 3. Operations ---
                elif mne in self.BIN_OP_MAP:
                    right = self._safe_pop(stack)
                    left = self._safe_pop(stack)
                    stack.append(BinaryOpNode(self.BIN_OP_MAP[mne], left, right))
                elif mne in self.UNARY_OP_MAP:
                    operand = self._safe_pop(stack)
                    stack.append(UnaryOpNode(self.UNARY_OP_MAP[mne], operand))
                elif mne in ('POST_INC', 'POST_DEC', 'PRE_INC', 'PRE_DEC'):
                    op_str = '++' if 'INC' in mne else '--'
                    is_post = 'POST' in mne

                    # [终极修复]: 检查是否有悬空的数组索引，防止索引被下一个变量错误吞噬
                    if pending_array_index is not None:
                        # 生成如 PlayerItem[7] 的节点
                        operand_node = ArrayAccessNode(VarNode(ops[0]), pending_array_index)
                        pending_array_index = None
                    else:
                        operand_node = VarNode(ops[0])

                    stack.append(UnaryOpNode(op_str, operand_node, is_postfix=is_post))

                # --- 4. Function Calls ---
                elif mne == 'ARG_COMMIT':
                    arg_val = self._safe_pop(stack)

                    # 剥离隐式传参赋值 (如 AddToValue_arg0 = "PlayerMoney")
                    # 并将其精准分发到对应函数的专属参数池中
                    if isinstance(arg_val, AssignNode) and arg_val.op == '=':
                        match = re.match(r'^([a-zA-Z0-9_]+)_arg(\d+)$', arg_val.target)
                        if match:
                            target_func = match.group(1)
                            arg_idx = int(match.group(2))
                            if target_func not in pending_func_args:
                                pending_func_args[target_func] = {}
                            pending_func_args[target_func][arg_idx] = arg_val.value
                            continue  # 成功隔离，直接进入下一条指令

                    # 如果不是标准命名，走后备方案
                    pending_args_fallback.append(arg_val)


                elif mne == 'CALL_FUNC':
                    raw_func_name = ops[0] if ops else mne
                    func_name = raw_func_name

                    match = re.match(r'^(?:Func_)?(\d+)$', raw_func_name, re.IGNORECASE)
                    if match:
                        func_id = int(match.group(1))
                        if func_id not in self.FUNC_DEF_MAP:
                            logger.error_and_stop(f"[AST-BUILDER] Missing Function definition for ID {func_id} at 0x{self.current_offset:X}. Using fallback '{raw_func_name}'.")
                        func_name = self.FUNC_DEF_MAP.get(func_id, raw_func_name)

                    args_to_pass = []
                    # 从专属参数池提取
                    if func_name in pending_func_args:
                        arg_dict = pending_func_args.pop(func_name)
                        args_to_pass = [arg_dict[idx] for idx in sorted(arg_dict.keys())]
                    elif raw_func_name in pending_func_args:
                        arg_dict = pending_func_args.pop(raw_func_name)
                        args_to_pass = [arg_dict[idx] for idx in sorted(arg_dict.keys())]
                    else:
                        args_to_pass = list(pending_args_fallback)
                        pending_args_fallback.clear()

                    # [修复]: 彻底删掉废弃的默认参数！
                    args_to_pass = [a for a in args_to_pass if
                                    not (isinstance(a, VarNode) and a.name == '__DUMMY_ARG__')]

                    stack.append(CallExprNode(func_name, args_to_pass))

                elif mne.startswith('CALL_EXT_'):
                    ext_id = int(mne.split('_')[-1])
                    if ext_id not in self.EXT_DEF_MAP:
                        logger.error_and_stop(f"[AST-BUILDER] Missing Extern Function definition for ID {ext_id} at 0x{self.current_offset:X}. Using fallback 'Unknown_Ext_{ext_id}'.")
                    func_name, arity = self.EXT_DEF_MAP.get(ext_id, (f"Unknown_Ext_{ext_id}", 1))
                    args = [self._safe_pop(stack) for _ in range(arity)][::-1]
                    # [修复]: 彻底删掉废弃的默认参数！
                    args = [a for a in args if not (isinstance(a, VarNode) and a.name == '__DUMMY_ARG__')]
                    stack.append(CallExprNode(func_name, args))

                # --- 5. Flow Control & Metadata ---
                elif mne in ('CAST_INT', 'CAST_STR'):
                    target_type = 'int' if mne == 'CAST_INT' else 'string'
                    operand = self._safe_pop(stack)
                    stack.append(CastNode(target_type, operand))

                elif mne in ('COMMA', 'LINE_NUM'):
                    while stack:
                        top = stack.pop()
                        if isinstance(top, (AssignNode, CallExprNode, UnaryOpNode)):
                            statements.append(ExprStmtNode(top))
                        else:
                            statements.append(AssignNode("Stack_Out", top))

                    if mne == 'LINE_NUM':
                        statements.append(LineNumNode(int(ops[0], 0)))

                elif mne in ('JMP_FALSE', 'IFF'):
                    statements.append(JumpNode(self._safe_pop(stack), self._parse_addr(ops[0]), mne))
                elif mne == 'JMP':
                    statements.append(JumpNode(None, self._parse_addr(ops[0]), mne))
                elif mne == 'RET':
                    ret_val = self._safe_pop(stack) if stack else None
                    statements.append(ReturnNode(ret_val))

            except Exception as e:
                logger.error_and_stop(f"[AST-BUILDER] Error at 0x{instr.offset:X}: {e}")

        while stack:
            top = stack.pop()
            if isinstance(top, (AssignNode, CallExprNode, UnaryOpNode)):
                statements.append(ExprStmtNode(top))
            else:
                statements.append(AssignNode("Stack_Out", top))

        return statements

    def _parse_addr(self, addr_str: str) -> int:
        return int(addr_str.split('_')[1], 16) if addr_str.startswith("loc_") else int(addr_str, 0)