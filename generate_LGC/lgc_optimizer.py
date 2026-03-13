"""
generate_LGC/lgc_optimizer.py
负责对反编译生成的伪代码进行文本级别的后处理和优化。
这些优化是必须的，因为没他们代码会有错误
"""

from logger import logger


class LgcOptimizer:
    """
    代码优化器类。
    提供静态方法用于清理和优化 AST 转换后残留的冗余代码或语法瑕疵。
    """

    @staticmethod
    def optimize(pseudo_code: str, method_name: str) -> str:
        """
        对生成的 AST 伪代码进行文本级优化和清洗。
        包含：清理双分号、处理末尾无意义的 return 占位符。

        :param pseudo_code: 由 AST 结构化折叠生成的原始伪代码字符串
        :param method_name: 当前正在处理的方法名（用于日志记录）
        :return: 清洗优化后的伪代码字符串
        """
        if not pseudo_code:
            return ""

        # 1. 清洗生成的 AST 残留双分号 (连续的两个分号替换为一个)
        code = pseudo_code.replace(";;", ";")

        # 2. 嗅探并注释掉方法末尾的无意义占位符 return;
        lines = code.split("\n")
        last_valid_idx = -1

        # 从后往前遍历，寻找最后一行实质性代码
        for j in range(len(lines) - 1, -1, -1):
            stripped = lines[j].strip()
            # 跳过空行和闭合大括号
            if not stripped or stripped == "}":
                continue
            last_valid_idx = j
            break

        # 如果最后一句实质代码恰好是 "return;"，将其注释掉并抛出警告
        if last_valid_idx != -1 and lines[last_valid_idx].strip() == "return;":
            lines[last_valid_idx] = lines[last_valid_idx].replace("return;", "// return; mark end of function")
            logger.warning(f"[LGC-OPTIMIZER] mark end of function 'return;' detected in {method_name}(), commented out.")

        return "\n".join(lines)