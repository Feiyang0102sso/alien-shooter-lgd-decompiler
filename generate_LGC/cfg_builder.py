"""
generate_LGC/cfg_builder.py
build the cfg object for each parsed objects
"""

from typing import List, Set, Optional
from logger import logger

from generate_LGC.asm_structs import AsmMethod, AsmInstruction
from generate_LGC.cfg_structs import BasicBlock


class CFGBuilder:
    def build_cfg(self, method: AsmMethod) -> List[BasicBlock]:
        if not method.instructions:
            logger.warning(f"[CFG-BUILDER] Method {method.name} is empty.")
            return []

        # 1. 识别“领头人” (Leaders)
        leaders = self._find_leaders(method)

        # 2. 根据 Leaders 切分指令
        blocks = self._create_blocks(method, leaders)

        # 3. 建立连接
        self._connect_blocks(blocks, method)

        # logger.info(f"[CFG-BUILDER]  CFG Built for '{method.name}': {len(blocks)} blocks.")
        return blocks

    def _find_leaders(self, method: AsmMethod) -> Set[int]:
        leaders = set()
        instructions = method.instructions

        # 规则1: 第一条指令是 Leader
        if instructions:
            leaders.add(instructions[0].offset)

        for i, instr in enumerate(instructions):
            mne = instr.mnemonic

            # --- 识别跳转指令及其目标 ---
            target_addr = None

            # 情况 A: 普通跳转 (JMP, JMP_FALSE, AND_JMP, OR_JMP) - 取第0个参数
            # if mne in ('JMP', 'JMP_FALSE', 'AND_JMP', 'OR_JMP'):
            if mne in ('JMP', 'JMP_FALSE'):
                target_addr = self._resolve_target_addr(method, instr, operand_idx=0)

            # 情况 B: IFF - 取第0个 和 第一个参数
            elif mne == 'IFF':
                false_branch = self._resolve_target_addr(method, instr, operand_idx=0)
                if false_branch is not None:
                    leaders.add(false_branch)
                cond_start = self._resolve_target_addr(method, instr, operand_idx=1)
                if cond_start is not None:
                    leaders.add(cond_start)

            # 情况 C: AWAIT - 取第0个参数 (未就绪时回跳的地址)
            elif mne == 'AWAIT':
                target_addr = self._resolve_target_addr(method, instr, operand_idx=0)

            # 规则2: 跳转的目标是 Leader
            if target_addr is not None:
                leaders.add(target_addr)

            # 规则3: 跳转/返回指令的**下一条**是 Leader
            # 包括 AWAIT 和 IFF，因为它们都是分支点
            is_terminator = mne in ('JMP', 'RET')
            # is_branch = mne in ('JMP_FALSE', 'AND_JMP', 'OR_JMP', 'IFF', 'AWAIT')
            is_branch = mne in ('JMP_FALSE', 'IFF', 'AWAIT')

            if is_terminator or is_branch:
                if i + 1 < len(instructions):
                    next_instr = instructions[i + 1]

                    if next_instr.mnemonic == 'LINE_NUM':
                        # 如果下一行是 LINE_NUM，让它黏在当前块。
                        # 并将 LINE_NUM 的再下一行（如果有）强制设为新块的 Leader！
                        if i + 2 < len(instructions):
                            leaders.add(instructions[i + 2].offset)
                    else:
                        # 如果下一行是普通指令，它直接成为新块的 Leader
                        leaders.add(next_instr.offset)

        return sorted(list(leaders))

    def _create_blocks(self, method: AsmMethod, leaders: List[int]) -> List[BasicBlock]:
        blocks = []
        if not leaders:
            return blocks

        # 优化：利用指令有序性一次遍历
        current_leader_idx = 0
        current_block_instrs = []
        current_block_start = leaders[0]

        for instr in method.instructions:
            # 检查是否到达下一个 Leader (切分点)
            if current_leader_idx + 1 < len(leaders):
                next_leader = leaders[current_leader_idx + 1]
                if instr.offset == next_leader:
                    # 保存当前块
                    if current_block_instrs:
                        bb = BasicBlock(id=len(blocks), start_offset=current_block_start,
                                        instructions=current_block_instrs)
                        blocks.append(bb)

                    # 开启新块
                    current_block_instrs = []
                    current_block_start = next_leader
                    current_leader_idx += 1

            current_block_instrs.append(instr)

        # 保存最后一个块
        if current_block_instrs:
            bb = BasicBlock(id=len(blocks), start_offset=current_block_start, instructions=current_block_instrs)
            blocks.append(bb)

        return blocks

    def _connect_blocks(self, blocks: List[BasicBlock], method: AsmMethod):
        addr_to_block = {b.start_offset: b for b in blocks}

        for block in blocks:
            if not block.instructions: continue

            # 如果结尾是 LINE_NUM，我们忽略它，向前找真正的指令
            effective_last_instr = block.instructions[-1]

            # 从后往前找，找到第一个非 LINE_NUM 的指令
            # 当然，如果整个块全是 LINE_NUM，那就只能用 LINE_NUM
            for i in range(len(block.instructions) - 1, -1, -1):
                if block.instructions[i].mnemonic != 'LINE_NUM':
                    effective_last_instr = block.instructions[i]
                    break

            mne = effective_last_instr.mnemonic

            # last_instr = block.instructions[-1]
            # mne = last_instr.mnemonic
            targets = []

            # --- 1. 计算 Explicit Target (跳转目标) ---
            jump_target = None

            # 普通跳转
            # if mne in ('JMP', 'JMP_FALSE', 'AND_JMP', 'OR_JMP'):
            if mne in ('JMP', 'JMP_FALSE'):
                jump_target = self._resolve_target_addr(method, effective_last_instr, operand_idx=0)

            # IFF: 0号参数是 False 分支 (跳过 Block)
            elif mne == 'IFF':
                jump_target = self._resolve_target_addr(method, effective_last_instr, operand_idx=0)

            # AWAIT: 0号参数是 Loop/Wait 分支
            elif mne == 'AWAIT':
                jump_target = self._resolve_target_addr(method, effective_last_instr, operand_idx=0)

            if jump_target is not None:
                targets.append(jump_target)

            # --- 2. 计算 Fall-through (自然下一行) ---
            # 只有 JMP and RET 绝对不往下走
            # IFF, AWAIT, JMP_FALSE 等如果条件不满足/满足，都会往下走
            has_fallthrough = True
            if mne == 'RET': has_fallthrough = False
            if mne == 'JMP': has_fallthrough = False

            if has_fallthrough:
                real_last = block.instructions[-1]
                next_addr = self._get_next_instr_addr(method, real_last)
                if next_addr is not None:
                    targets.append(next_addr)

            # --- 3. 执行连接 ---
            for t_addr in targets:
                target_block = addr_to_block.get(t_addr)
                if target_block:
                    block.successors.append(target_block)
                    target_block.predecessors.append(block)
                else:
                    # 异常处理：跳转到了一个不存在 Block 的地址 (可能切分逻辑有误，或者跳转到了指令中间)
                    logger.error(
                        f"[CFG-BUILDER] Method {method.name}: Block {block.id} tries to jump to 0x{t_addr:X}, but no block starts there.")
                    # raise

    def _resolve_target_addr(self, method: AsmMethod, instr: AsmInstruction, operand_idx: int) -> Optional[int]:
        """
        统一处理地址计算，支持 loc_XXXX 和 0xOffset 两种格式
        并进行越界检查
        """
        try:
            if operand_idx >= len(instr.operands):
                return None

            op_str = instr.operands[operand_idx]
            target = None

            # 情况 1: 标签格式 "loc_0C43" -> 绝对地址 0x0C43
            if op_str.startswith("loc_"):
                hex_str = op_str.split('_')[1]
                target = int(hex_str, 16)

            # 情况 2: 偏移量格式 "0x1A" -> 相对地址 Addr + 1 + Offset
            else:
                offset_val = int(op_str, 0)
                target = instr.offset + 1 + offset_val

            # 异常检查: 目标地址必须存在于方法内
            if target is not None:
                if target not in method.addr_map:
                    logger.error(
                        f"[CFG-BUILDER] Method {method.name}: Instruction at 0x{instr.offset:X} ({instr.mnemonic}) targets 0x{target:X}, which is out of bounds.")
                    return None
                return target

        except Exception as e:
            logger.error(f"[CFG-BUILDER] Error resolving target for {instr}: {e}")
            # raise
            return None

        return None

    def _get_next_instr_addr(self, method: AsmMethod, instr: AsmInstruction) -> Optional[int]:
        # 简单高效的获取下一条指令地址的方法：利用列表索引
        # 如果追求极致性能，可以在 parse 阶段给 instr 增加 next 属性
        try:
            # 注意：index() 在大列表中可能稍慢，但对于一般函数大小可接受
            # 如果想优化，可以使用 instr.offset 在 addr_map 找，然后找 sorted keys 的下一个，但也慢
            # 目前最稳妥是 index
            idx = method.instructions.index(instr)
            if idx + 1 < len(method.instructions):
                return method.instructions[idx + 1].offset
        except ValueError:
            pass
        return None