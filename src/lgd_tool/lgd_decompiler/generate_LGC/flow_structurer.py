"""
generate_LGC/flow_structurer.py
Analyzes the flat CFG and structures it into High-Level constructs (If/While).
"""
import re
from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple

from lgd_tool.lgd_decompiler.generate_LGC.cfg_structs import BasicBlock


# ==========================================
# 1. 图论分析辅助数据结构
# ==========================================
@dataclass
class LoopInfo:
    """用于在图论分析阶段记录循环信息的纯数据结构"""
    header: BasicBlock
    body_blocks: Set[int]
    back_edges: List[Tuple[BasicBlock, BasicBlock]]


# ==========================================
# 2. 高级控制流结构 (Regions)
# ==========================================
class Region:
    def to_code(self, indent: int = 0) -> str:
        raise NotImplementedError


@dataclass
class BlockRegion(Region):
    block: 'BasicBlock'

    def to_code(self, indent: int = 0) -> str:
        prefix = "    " * indent
        lines = []
        for stmt in getattr(self.block, 'statements', []):
            code = stmt.to_code()
            if code.startswith("goto ") or code.startswith("if ("):
                continue
            lines.append(f"{prefix}{code}")
        return "\n".join(lines) if lines else ""


@dataclass
class LoopRegion(Region):
    header_block: 'BasicBlock'
    body_region: Region
    cond_str: str = "1"

    def to_code(self, indent: int = 0) -> str:
        prefix = "    " * indent
        res = f"{prefix}while ({self.cond_str}) {{\n"
        res += self.body_region.to_code(indent + 1) + "\n"
        res += f"{prefix}}}"
        return res


@dataclass
class DoWhileRegion(Region):
    body_region: Region
    cond_str: str

    def to_code(self, indent: int = 0) -> str:
        prefix = "    " * indent
        res = f"{prefix}do {{\n"
        res += self.body_region.to_code(indent + 1) + "\n"
        res += f"{prefix}}} while ({self.cond_str});"
        return res


@dataclass
class IfRegion(Region):
    cond_block: 'BasicBlock'
    then_region: Region
    else_region: Optional[Region]
    cond_str: str = "Condition"
    is_iff: bool = False
    is_elif: bool = False

    def to_code(self, indent: int = 0) -> str:
        prefix = "    " * indent

        # ==========================================
        # 1. 处理特殊的 iff 逻辑
        # ==========================================
        if self.is_iff:
            res = f"{prefix}iff ({self.cond_str}) {{\n"
            res += self.then_region.to_code(indent + 1) + "\n"
            res += f"{prefix}}}"

            # 如果因为内部有 return 导致 CFG 识别出了 else_region，
            # 直接将其作为正常的后续顺序代码平铺在下方
            if self.else_region:
                else_code = self.else_region.to_code(indent)
                if else_code.strip():
                    res += "\n" + else_code
            return res

        # ==========================================
        # 2. 生成标准的 if 头部和 then 分支
        # ==========================================
        if self.is_elif:
            res = f"if ({self.cond_str}) {{\n"
        else:
            res = f"{prefix}if ({self.cond_str}) {{\n"

        then_code = self.then_region.to_code(indent + 1)
        res += then_code + "\n"

        # ==========================================
        # [优化]: 提前返回 (Early Return) 展平机制！
        # 嗅探 then 分支的最后一条有效代码，如果是终结语句，则撕掉 else 包装
        # ==========================================
        lines = [l.strip() for l in then_code.split('\n') if l.strip()]
        # 过滤掉行号等注释，找出真正的代码语句
        code_lines = [l for l in lines if not l.startswith('//')]
        is_terminating = False
        if code_lines:
            last_stmt = code_lines[-1]
            # 探测 return, break, 或底层的 goto
            if last_stmt.startswith("return") or last_stmt.startswith("break;") or last_stmt.startswith("goto "):
                is_terminating = True

        # 如果满足展平条件，直接将 else 代码作为顺序逻辑平铺在下方！
        if is_terminating:
            res += f"{prefix}}}"
            if self.else_region:
                else_code = self.else_region.to_code(indent)
                if else_code.strip():
                    res += "\n" + else_code
            return res

        # ==========================================
        # 3. 处理正常的 else / else if 逻辑
        # ==========================================
        if self.else_region and isinstance(self.else_region, SeqRegion):

            # [修复]: 避免对复合 Region 进行 to_code(0) 深层展开，防止 O(2^N) 性能爆炸！
            valid_regs = []
            for r in self.else_region.regions:
                if isinstance(r, BlockRegion):
                    if r.to_code(0).strip():  # 只有基本块才需要试探性生成看是不是空的
                        valid_regs.append(r)
                else:
                    # 对于 IfRegion, LoopRegion 等复合结构，认为其一定有内容，直接纳入
                    valid_regs.append(r)

            # 识别 Else-If 链
            if len(valid_regs) == 1 and isinstance(valid_regs[0], IfRegion):
                elif_reg: IfRegion = valid_regs[0]  # 类型断言
                if not elif_reg.is_iff:
                    elif_reg.is_elif = True
                    res += f"{prefix}}} else " + elif_reg.to_code(indent)
                else:
                    # 如果后续是一个 iff，不能用 else 连着，必须写成标准的 else { iff }
                    res += f"{prefix}}} else {{\n"
                    res += self.else_region.to_code(indent + 1) + "\n"
                    res += f"{prefix}}}"
            elif valid_regs:
                res += f"{prefix}}} else {{\n"
                res += self.else_region.to_code(indent + 1) + "\n"
                res += f"{prefix}}}"
            else:
                res += f"{prefix}}}"
        else:
            res += f"{prefix}}}"

        return res


@dataclass
class SeqRegion(Region):
    regions: List[Region] = field(default_factory=list)

    def to_code(self, indent: int = 0) -> str:
        lines = []
        skip_set = set()

        for i in range(len(self.regions)):
            if i in skip_set:
                continue

            r = self.regions[i]

            # ==========================================
            # [核心优化]: 严谨的 For 循环提升 (跨越幽灵块 + 严格同源行号)
            # ==========================================
            if isinstance(r, BlockRegion):
                block_code = r.to_code(0).strip()
                if block_code:
                    next_idx = i + 1
                    loop_reg = None
                    while next_idx < len(self.regions):
                        next_r = self.regions[next_idx]
                        if isinstance(next_r, LoopRegion):
                            loop_reg = next_r
                            break
                        elif isinstance(next_r, BlockRegion) and not next_r.to_code(0).strip():
                            next_idx += 1
                        else:
                            break

                    if loop_reg:
                        block_lines = block_code.split('\n')
                        body_lines = loop_reg.body_region.to_code(0).strip().split('\n')

                        # 1. 探测初始化语句及其行号 (从下往上扫)
                        actual_init_idx = -1
                        init_stmt = ""
                        init_var = ""
                        init_line = ""
                        for idx in range(len(block_lines) - 1, -1, -1):
                            line = block_lines[idx].strip()
                            if line.startswith("// --- Line "):
                                if not init_stmt: init_line = line  # 记录紧跟在语句下方的行号
                            elif line and "=" in line and "==" not in line:
                                init_stmt = line
                                actual_init_idx = idx
                                init_var = line.split("=")[0].strip()
                                break

                        # 2. 探测步进器语句及其行号 (从下往上扫)
                        actual_step_idx = -1
                        step_stmt = ""
                        step_line = ""
                        for idx in range(len(body_lines) - 1, -1, -1):
                            line = body_lines[idx].strip()
                            if line.startswith("// --- Line "):
                                if not step_stmt: step_line = line  # 记录紧跟在语句下方的行号
                            elif line and any(op in line for op in ["++", "--", "+=", "-="]):
                                step_stmt = line
                                actual_step_idx = idx
                                break

                        # 3. 极度严谨的 For 循环校验条件
                        is_for_loop = False
                        if init_stmt and step_stmt and init_var and (init_var in step_stmt):
                            # 【真理时刻】：只有行号完全相同，才提升为 for！
                            if init_line and step_line and init_line == step_line:
                                is_for_loop = True

                        if is_for_loop:
                            init_str = init_stmt.replace(";", "")
                            cond_str = loop_reg.cond_str
                            step_str = step_stmt.replace(";", "")

                            prefix = "    " * indent

                            # 打印 init 语句之前的所有其他准备代码
                            for idx in range(actual_init_idx):
                                line = block_lines[idx].strip()
                                if line: lines.append(f"{prefix}{line}")

                            # 组装霸气的 For 循环头部
                            lines.append(f"{prefix}for ({init_str}; {cond_str}; {step_str}) {{")

                            # 提取干净的循环体 (剔除底部的步进器和它附带的行号)
                            for idx in range(len(body_lines)):
                                if idx == actual_step_idx: continue
                                if idx > actual_step_idx and step_line and body_lines[
                                    idx].strip() == step_line: continue
                                line = body_lines[idx].strip()
                                if line: lines.append(f"    {prefix}{line}")

                            lines.append(f"{prefix}}}")

                            for skip_i in range(i, next_idx + 1):
                                skip_set.add(skip_i)
                            continue

            # 普通区域直接打印
            code = r.to_code(indent)
            if str(code).strip():
                lines.append(code)

        return "\n".join(lines)

@dataclass
class BreakRegion(Region):
    def to_code(self, indent: int = 0) -> str:
        return "    " * indent + "break;"


@dataclass
class AwaitRegion(Region):
    body_region: Region

    def to_code(self, indent: int = 0) -> str:
        prefix = "    " * indent
        # 获取内部代码 (比如 "finishResourcesLoad();")
        body_code = self.body_region.to_code(0).strip()

        # 剥离多余的换行和结尾的分号，以便包裹进 await() 里
        if body_code.endswith(";"):
            body_code = body_code[:-1]
        body_code = body_code.replace('\n', ' ')

        return f"{prefix}await({body_code});"

# ==========================================
# 3. 控制流结构化主类
# ==========================================
class FlowStructurer:
    def __init__(self, blocks: List[BasicBlock]):
        self.blocks = blocks
        self.entry_block = blocks[0] if blocks else None

        self.dominators: Dict[int, Set[int]] = {}
        self.idom: Dict[int, Optional[int]] = {}
        self.post_dominators: Dict[int, Set[int]] = {}
        self.ipdom: Dict[int, Optional[int]] = {}

        self.loops: List[LoopInfo] = []
        self.if_regions: List[IfRegion] = []

    def build_structure(self):
        if not self.blocks:
            return

        # print("\n[FlowStructurer] 1. Computing Dominators...")
        self._compute_dominators()
        # self._print_dominators()

        # print("\n[FlowStructurer] 2. Identifying Loops...")
        self._find_loops()

        # print("\n[FlowStructurer] 3. Computing Post-Dominators...")
        self._compute_post_dominators()

        # print("\n[FlowStructurer] 4. Folding Regions...")
        # self._structure_regions() #

    def _compute_dominators(self):
        if not self.blocks: return
        reachable_ids = set()
        stack = [self.entry_block]
        while stack:
            curr = stack.pop()
            if curr.id not in reachable_ids:
                reachable_ids.add(curr.id)
                stack.extend(curr.successors)

        for b in self.blocks:
            if b.id not in reachable_ids:
                self.dominators[b.id] = {b.id}
                self.idom[b.id] = None
            elif b == self.entry_block:
                self.dominators[b.id] = {b.id}
            else:
                self.dominators[b.id] = set(reachable_ids)

        changed = True
        while changed:
            changed = False
            for b in self.blocks:
                if b == self.entry_block or b.id not in reachable_ids: continue
                valid_preds = [p for p in b.predecessors if p.id in reachable_ids]
                if valid_preds:
                    pred_doms = [self.dominators[p.id] for p in valid_preds]
                    intersected = set.intersection(*pred_doms)
                else:
                    intersected = set()
                new_dom = intersected.copy()
                new_dom.add(b.id)
                if new_dom != self.dominators[b.id]:
                    self.dominators[b.id] = new_dom
                    changed = True

        for b in self.blocks:
            if b == self.entry_block or b.id not in reachable_ids: continue
            strict_doms = self.dominators[b.id] - {b.id}
            for candidate in strict_doms:
                is_idom = True
                for other in strict_doms:
                    if other == candidate: continue
                    if candidate in self.dominators[other]:
                        is_idom = False
                        break
                if is_idom:
                    self.idom[b.id] = candidate
                    break

    def _print_dominators(self):
        for b in self.blocks:
            doms_str = ", ".join(map(str, sorted(list(self.dominators[b.id]))))
            idom_str = str(self.idom.get(b.id, "None"))
            print(f"  Block {b.id:2d} | IDom: {idom_str:4s} | Dominated by: [{doms_str}]")

    def _find_loops(self):
        if not self.blocks: return
        back_edges = []
        for block in self.blocks:
            for succ in block.successors:
                if succ.id in self.dominators.get(block.id, set()):
                    back_edges.append((block, succ))

        loops_dict: Dict[int, LoopInfo] = {}
        for tail, header in back_edges:
            if header.id not in loops_dict:
                loops_dict[header.id] = LoopInfo(header=header, body_blocks=set(), back_edges=[])
            loop = loops_dict[header.id]
            loop.back_edges.append((tail, header))
            loop.body_blocks.add(header.id)

            if tail.id != header.id:
                if tail.id not in loop.body_blocks:
                    loop.body_blocks.add(tail.id)
                    stack = [tail]
                    while stack:
                        curr = stack.pop()
                        for pred in curr.predecessors:
                            if pred.id not in loop.body_blocks:
                                loop.body_blocks.add(pred.id)
                                stack.append(pred)

        self.loops = list(loops_dict.values())

    def _compute_post_dominators(self):
        if not self.blocks: return
        exit_blocks = [b for b in self.blocks if not b.successors]
        if not exit_blocks: exit_blocks = [self.blocks[-1]]

        rev_reachable = set()
        stack = [b for b in exit_blocks]
        while stack:
            curr = stack.pop()
            if curr.id not in rev_reachable:
                rev_reachable.add(curr.id)
                stack.extend(curr.predecessors)

        for b in self.blocks:
            if b.id not in rev_reachable:
                self.post_dominators[b.id] = {b.id}
                self.ipdom[b.id] = None
            elif b in exit_blocks:
                self.post_dominators[b.id] = {b.id}
            else:
                self.post_dominators[b.id] = set(rev_reachable)

        changed = True
        while changed:
            changed = False
            for b in self.blocks:
                if b in exit_blocks or b.id not in rev_reachable: continue
                valid_succs = [s for s in b.successors if s.id in rev_reachable]
                if valid_succs:
                    succ_pdoms = [self.post_dominators[s.id] for s in valid_succs]
                    intersected = set.intersection(*succ_pdoms)
                else:
                    intersected = set()
                new_pdom = intersected.copy()
                new_pdom.add(b.id)
                if new_pdom != self.post_dominators[b.id]:
                    self.post_dominators[b.id] = new_pdom
                    changed = True

        for b in self.blocks:
            if b in exit_blocks or b.id not in rev_reachable: continue
            strict_pdoms = self.post_dominators[b.id] - {b.id}
            if not strict_pdoms:
                self.ipdom[b.id] = None
                continue
            closest_pdom = max(strict_pdoms, key=lambda c: len(self.post_dominators[c]))
            self.ipdom[b.id] = closest_pdom

    def _extract_condition(self, block: BasicBlock) -> str:
        if not hasattr(block, 'statements') or not block.statements:
            return "1"
        for stmt in reversed(block.statements):
            code = stmt.to_code()
            if code.startswith("if ("):
                m = re.search(r'if \([A-Z_]+:\s*(.+)\)\s*goto', code)
                if m:
                    cond = m.group(1)
                    if cond.startswith('(!(') and cond.endswith('))'):
                        cond = cond[3:-2]
                    return cond
        return "1"

    def _get_true_false_blocks(self, block: BasicBlock) -> Tuple[Optional[BasicBlock], Optional[BasicBlock]]:
        if not block.successors: return None, None
        if len(block.successors) == 1: return block.successors[0], None
        last_instr = next((i for i in reversed(block.instructions) if i.mnemonic != 'LINE_NUM'), None)
        if not last_instr: return block.successors[1], block.successors[0]
        mne = last_instr.mnemonic
        succ0, succ1 = block.successors[0], block.successors[1]
        if mne in ('JMP_FALSE', 'IFF', 'AND_JMP'): return succ1, succ0
        elif mne in ('OR_JMP',): return succ0, succ1
        else: return succ1, succ0

    def fold_into_tree(self) -> Region:
        if not self.blocks: return SeqRegion([])
        # print("\n[FlowStructurer] 5. Generating Abstract Code Tree...")
        return self._build_region(self.entry_block, stop_blocks=set())

    def _build_region(self, current_block: 'BasicBlock', stop_blocks: Set[int], processed_loops: Set[int] = None,
                      path_stack: Set[int] = None, active_loop_exits: Set[int] = None) -> Region:
        if processed_loops is None: processed_loops = set()
        if path_stack is None: path_stack = set()  # [NEW] 递归追踪防爆盾
        if active_loop_exits is None: active_loop_exits = set()  # [NEW] 记录当前层级所有合法的循环出口

        seq = SeqRegion()
        curr = current_block
        loop_headers = {loop.header.id: loop for loop in self.loops}
        visited = set()
        is_first_block = True

        while curr is not None:
            if not is_first_block and curr.id in stop_blocks:
                break
                
            is_first_block = False

            if curr.id in visited:
                break

            # ==========================================
            # 终极死循环断路器
            # 如果当前块已经在上层的递归路径中，说明遭遇了不可规约的奇葩死循环。
            # 直接切断递归
            # ==========================================
            if curr.id in path_stack:
                # 默默打断即可，生成的代码会在这里直接顺延到末尾
                break

            visited.add(curr.id)
            # 把自己加入路径记录，传给深层的子分支
            next_path_stack = path_stack | {curr.id}

            if curr.id in loop_headers and curr.id not in processed_loops:
                processed_loops.add(curr.id)
                loop_info = loop_headers[curr.id]
                
                # ============== 强制捕捉 AWAIT 宏 ==============
                last_instr = next((i for i in reversed(curr.instructions) if i.mnemonic != 'LINE_NUM'), None)
                if last_instr and last_instr.mnemonic == 'AWAIT':
                    seq.regions.append(AwaitRegion(BlockRegion(curr)))
                    exit_blocks = [s for s in curr.successors if s.id not in loop_info.body_blocks]
                    curr = exit_blocks[0] if exit_blocks else None
                    continue

                # A loop is a while-loop (header exits) if any successor goes outside loop body
                exit_from_header = [s for s in curr.successors if s.id not in loop_info.body_blocks]
                is_while_loop = len(exit_from_header) > 0

                if not is_while_loop:
                    # Treat as do-while or robust while(1) loop
                    loop_exits = set()
                    for bid in loop_info.body_blocks:
                        b = next((x for x in self.blocks if x.id == bid), None)
                        if b:
                            for s in b.successors:
                                if s.id not in loop_info.body_blocks:
                                    loop_exits.add(s.id)
                    
                    exit_block = None
                    if loop_exits:
                        exit_block_id = list(loop_exits)[0]
                        exit_block = next((x for x in self.blocks if x.id == exit_block_id), None)
                    
                    loop_stops = stop_blocks.copy()
                    if exit_block: 
                        loop_stops.add(exit_block.id)

                    next_loop_exits = active_loop_exits.copy()
                    for e in loop_exits:
                        next_loop_exits.add(e)

                    # Extract the condition of the single-block do-while if possible to maintain old style
                    if len(loop_info.body_blocks) == 1:
                        cond_str = self._extract_condition(curr)
                        body_reg = SeqRegion([BlockRegion(curr)])
                        seq.regions.append(DoWhileRegion(body_reg, cond_str))
                    else:
                        # Multi-block robust while(1) processing
                        loop_stops.add(curr.id)
                        next_path_stack = path_stack.copy()
                        body_region = self._build_region(curr, loop_stops, processed_loops.copy(), next_path_stack, next_loop_exits)
                        seq.regions.append(LoopRegion(curr, body_region, "1"))
                        
                    curr = exit_block
                else:
                    cond_str = self._extract_condition(curr)
                    true_block, false_block = self._get_true_false_blocks(curr)
                    exit_block = false_block if false_block and false_block.id not in loop_info.body_blocks else true_block
                    body_start = true_block if true_block and true_block.id in loop_info.body_blocks else false_block

                    loop_stops = stop_blocks.copy()
                    loop_stops.add(curr.id)
                    if exit_block: loop_stops.add(exit_block.id)

                    seq.regions.append(BlockRegion(curr))
                    if body_start:
                        # [传递防爆盾] 外加 强制拷贝 processed_loops 阻断状态泄漏
                        next_loop_exits = active_loop_exits.copy()
                        if exit_block: next_loop_exits.add(exit_block.id)

                        # body_region = self._build_region(body_start, loop_stops, processed_loops, next_path_stack, next_loop_exits)
                        # seq.regions.append(LoopRegion(curr, body_region, cond_str))
                        body_region = self._build_region(body_start, loop_stops, processed_loops.copy(),
                                                         next_path_stack, next_loop_exits)
                        seq.regions.append(LoopRegion(curr, body_region, cond_str))
                    curr = exit_block
                continue


            elif len(curr.successors) > 1:
                true_block, false_block = self._get_true_false_blocks(curr)
                # ==========================================
                # [终极修复]: 启用结构化启发式合并探测
                # ==========================================
                t_id = true_block.id if true_block else None
                f_id = false_block.id if false_block else None
                merge_id = None
                if t_id is not None and f_id is not None:
                    merge_id = self._find_structural_merge(curr.id, t_id, f_id)
                else:
                    merge_id = self.ipdom.get(curr.id)

                branch_stops = stop_blocks.copy()
                if merge_id is not None:
                    branch_stops.add(merge_id)
                cond_str = self._extract_condition(curr)
                last_instr = next((i for i in reversed(curr.instructions) if i.mnemonic != 'LINE_NUM'), None)
                is_iff = last_instr and last_instr.mnemonic == 'IFF'
                then_reg = SeqRegion()
                else_reg = None
                if true_block:
                    if true_block.id in active_loop_exits:
                        then_reg.regions.append(BreakRegion())
                    elif true_block.id not in branch_stops:
                        then_reg = self._build_region(true_block, branch_stops, processed_loops.copy(), next_path_stack,
                                                      active_loop_exits)

                if false_block:
                    if false_block.id in active_loop_exits:
                        else_reg = SeqRegion([BreakRegion()])
                    elif false_block.id not in branch_stops:
                        else_reg = self._build_region(false_block, branch_stops, processed_loops.copy(),
                                                      next_path_stack, active_loop_exits)

                seq.regions.append(BlockRegion(curr))
                seq.regions.append(IfRegion(curr, then_reg, else_reg, cond_str, is_iff=is_iff))
                curr = next((b for b in self.blocks if b.id == merge_id), None) if merge_id is not None else None
                continue

            else:
                seq.regions.append(BlockRegion(curr))
                # ==========================================
                # 优化: 探测并生成 Break
                # 如果当前块的最后一条指令是 JMP，且目标是活跃循环的出口，就是 break
                # ==========================================
                if curr.instructions:
                    last_instr = next((i for i in reversed(curr.instructions) if i.mnemonic != 'LINE_NUM'), None)
                    if last_instr and last_instr.mnemonic == 'JMP':
                        if curr.successors and len(curr.successors) == 1:
                            target_id = curr.successors[0].id
                            if target_id in active_loop_exits:
                                seq.regions.append(BreakRegion())

                curr = curr.successors[0] if curr.successors else None

        return seq

    def _find_structural_merge(self, curr_id: int, t_id: int, f_id: int) -> Optional[int]:
        """
        [防爆盾核心] 启发式寻找物理合并点。
        绕过提前 return 破坏的后向支配树，强制寻找最接近的物理合并块，防止 AST 生成时的指数级裂变。
        """
        block_map = {b.id: b for b in self.blocks}

        # 1. 探索 True 分支的前向可达块
        t_reachable = {t_id}
        queue = [t_id]
        while queue:
            curr = queue.pop(0)
            block = block_map.get(curr)
            if block:
                for s in block.successors:
                    # 仅前向探索，避免陷入死循环背边
                    if s.id not in t_reachable and s.start_offset > block.start_offset:
                        t_reachable.add(s.id)
                        queue.append(s.id)

        if f_id in t_reachable:
            return f_id  # True 分支会掉落到 False 分支 (这是一个纯粹的 If-Then)

        # 2. 探索 False 分支的前向可达块
        f_reachable = {f_id}
        queue = [f_id]
        while queue:
            curr = queue.pop(0)
            block = block_map.get(curr)
            if block:
                for s in block.successors:
                    if s.id not in f_reachable and s.start_offset > block.start_offset:
                        f_reachable.add(s.id)
                        queue.append(s.id)

        if t_id in f_reachable:
            return t_id  # 倒置的条件

        # 3. 如果都没有直接掉落，寻找最近的共同交点
        intersection = t_reachable.intersection(f_reachable)
        if intersection:
            # 找到在汇编物理布局上最接近两者的交点
            return min(intersection, key=lambda x: block_map[x].start_offset)

        # 实在找不到，只能回退求助 ipdom
        return self.ipdom.get(curr_id)