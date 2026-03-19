"""
generate_LGC/lgc_optimizer.py
负责对反编译生成的伪代码进行文本级别的后处理和优化。
这些优化是必须的，因为没他们代码会有错误
"""

from lgd_tool.logger import logger


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

    @staticmethod
    def merge_array_element_assigns(pseudo_code: str, local_arrays: list, func_name: str) -> tuple:
        """
        提取非 static 数组的逐元素赋值，从函数体中移除，并返回初始化值映射。

        编译器会把非 static 局部数组的每个元素当作独立变量逐个赋值，例如：
            main_local16 = 1;
            main_local17 = 2;
        本方法将这些赋值行从函数体中删除，并返回 {数组名: 初始化字符串} 映射表，
        由调用方合并到变量声明区。同时去重因移除赋值而产生的连续重复 line 注释。

        :param pseudo_code: 伪代码字符串
        :param local_arrays: 非 static 数组元数据列表，每项包含 name/start_index/size/type
        :param func_name: 函数名（用于构造变量名前缀）
        :return: (修改后的伪代码, {数组名: "{ val1, val2, ... }"})
        """
        if not pseudo_code or not local_arrays:
            return pseudo_code, {}

        # 构建 element_index -> array_meta 的映射
        element_to_array = {}
        for arr in local_arrays:
            start = arr["start_index"]
            size = arr["size"]
            for offset in range(size):
                element_to_array[start + offset] = arr

        # 第一遍：移除数组元素赋值行，收集初始化值
        lines = pseudo_code.split("\n")
        kept_lines = []
        array_inits = {}

        for line in lines:
            stripped = line.strip()
            arr_meta = LgcOptimizer._match_array_element_assign(stripped, func_name, element_to_array)

            if arr_meta is None:
                kept_lines.append(line)
                continue

            # 数组元素赋值 -> 收集值，不输出此行
            arr_name = arr_meta["name"]
            value = LgcOptimizer._extract_assign_value(stripped)
            if arr_name not in array_inits:
                array_inits[arr_name] = []
            array_inits[arr_name].append(value)

        # 第二遍：去重连续重复的 line 注释（如多个 // --- Line 7 ---）
        result = []
        prev_stripped = None
        for line in kept_lines:
            stripped = line.strip()
            is_line_comment = stripped.startswith("// --- Line") and stripped.endswith("---")
            if is_line_comment and stripped == prev_stripped:
                continue
            prev_stripped = stripped if is_line_comment else None
            result.append(line)

        # 格式化初始化值字符串
        if array_inits:
            merged_names = ", ".join(array_inits.keys())
            logger.debug(f"[LGC-OPTIMIZER] Merged element assigns into declarations for: {merged_names} in {func_name}()")

        formatted_inits = {}
        for name, values in array_inits.items():
            init_str = ", ".join(values)
            formatted_inits[name] = f"{{ {init_str} }}"

        return "\n".join(result), formatted_inits

    @staticmethod
    def _match_array_element_assign(stripped: str, func_name: str, element_to_array: dict):
        """
        判断一行是否是数组元素赋值语句（如 main_local16 = 1;）。
        如果是，返回对应的数组元数据；否则返回 None。
        """
        if "=" not in stripped or not stripped.endswith(";"):
            return None

        parts = stripped.split("=", 1)
        var_name = parts[0].strip()

        prefix = f"{func_name}_local"
        if not var_name.startswith(prefix):
            return None

        suffix = var_name[len(prefix):]
        if not suffix.isdigit():
            return None

        idx = int(suffix)
        return element_to_array.get(idx)

    @staticmethod
    def _extract_assign_value(stripped: str) -> str:
        """从赋值语句中提取右值。例如 'main_local16 = 1;' -> '1'"""
        parts = stripped.split("=", 1)
        if len(parts) != 2:
            return None
        value = parts[1].strip()
        if value.endswith(";"):
            value = value[:-1].strip()
        return value