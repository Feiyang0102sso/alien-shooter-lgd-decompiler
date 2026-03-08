"""
generate_LGC/lgc_context.py
负责加载 CSV 映射表，构建和维护全局环境上下文，解析变量、参数与局部变量。
"""

import os
import csv
import json
from typing import List, Dict, Tuple
from generate_LGC.lgc_header_manager import LgcHeaderManager
from logger import logger


class LgcContext:
    """
    LGC 项目上下文类。
    负责从 CSV 文件加载所有外部符号、全局变量、函数定义及其参数和局部变量。
    """

    def __init__(self):
        """初始化上下文，准备各类映射表，并实例化 Header 管理器。"""
        # 外部函数映射表: {Extern_ID: (Name, Size)}
        self.ext_map: Dict[int, Tuple[str, int]] = {}
        # 内部函数映射表: {Global_ID: Name}
        self.func_map: Dict[int, str] = {}

        # 函数参数列表字典: {"FuncName": ["int arg0", "string arg1=\"A\""]}
        self.func_params: Dict[str, List[str]] = {}
        # 函数局部变量列表字典: {"FuncName": ["int local0;", "static int local1 = 0;"]}
        self.func_locals: Dict[str, List[str]] = {}

        # 引入专用的 Header 管理器
        self.header_manager = LgcHeaderManager()

    def _parse_bool(self, val: any) -> bool:
        """内部辅助方法：安全地解析布尔值。"""
        return str(val).strip().lower() in {"true", "1", "yes", "on"}

    def _escape_string(self, raw_str: any) -> str:
        """
        内部辅助方法：安全转义字符串中的反斜杠和双引号。
        专门用于绕过 Python 3.10 中 f-string 不能包含反斜杠的限制。
        """
        return str(raw_str).replace('\\', '\\\\').replace('"', '\\"')

    def load_from_csv(self, csv_path: str) -> None:
        """从指定的 CSV 文件读取配置，分类填充到上下文中，并执行严格的错误校验。"""
        if not os.path.exists(csv_path):
            logger.error_and_stop(f"[LGC-CONTEXT] Error: CSV map file '{csv_path}' not found. Decompilation may fail.")
            return

        logger.info(f"[LGC-CONTEXT] Loading context from '{csv_path}'...")

        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader, start=2):  # header is row 1
                cat = row.get('Category', '').lstrip('\t').strip()
                name = row.get('Name', '').lstrip('\t').strip()

                if not cat or not name:
                    logger.error_and_stop(f"[LGC-CONTEXT] Row {row_idx}: Missing 'Category' or 'Name'. Skipped. Row data: {row}")
                    continue

                is_array = self._parse_bool(row.get('Is_Array', '').lstrip('\t'))
                is_init = self._parse_bool(row.get('Is_Initialized', '').lstrip('\t'))
                raw_val = row.get('Init_Value', 'N/A').lstrip('\t')
                if raw_val == '':
                    raw_val = 'N/A'
                size_str = row.get('Size', '1').lstrip('\t')

                # --- 1. 解析 EXTERN (外部函数) ---
                if cat == 'EXTERN':
                    try:
                        ext_id_str = row.get('Extern_ID', '').lstrip('\t')
                        if not ext_id_str.isdigit():
                            raise ValueError(f"Invalid or missing Extern_ID: '{ext_id_str}'")

                        ext_id = int(ext_id_str)
                        size_int = int(size_str) if size_str.isdigit() else 1
                        self.ext_map[ext_id] = (name, size_int)

                        # 参数推迟到所有的 PARAM 行解析完毕后，集中生成 EXTERN 文件头
                        if name not in self.func_params:
                            self.func_params[name] = []

                    except Exception as e:
                        logger.error_and_stop(f"[LGC-CONTEXT] EXTERN parse error at row {row_idx} ({name}): {e}")

                # --- 2. 解析 VAR (全局变量) ---
                elif cat == 'VAR':
                    g_type = row.get('Type', 'int').lstrip('\t')
                    if is_array:
                        if not is_init or raw_val in ('N/A', ''):
                            self.header_manager.add_global(f"{g_type} {name}[{size_str}];")
                        else:
                            try:
                                val_list = json.loads(raw_val)
                                formatted_vals = []
                                for v in val_list:
                                    if g_type == 'string':
                                        safe_str = self._escape_string(v)
                                        formatted_vals.append(f'"{safe_str}"')
                                    else:
                                        formatted_vals.append(str(v))

                                init_str = ', '.join(formatted_vals)
                                self.header_manager.add_global(f"{g_type} {name}[{size_str}] = {{ {init_str} }};")
                            except json.JSONDecodeError as e:
                                logger.error_and_stop(f"[LGC-CONTEXT] VAR array JSON decode error at row {row_idx} ({name}): {e}")
                                self.header_manager.add_global(f"{g_type} {name}[{size_str}]; // Init failed")
                    else:
                        if not is_init or raw_val in ('N/A', ''):
                            self.header_manager.add_global(f"{g_type} {name};")
                        else:
                            if g_type == 'string' and not raw_val.startswith('"'):
                                safe_str = self._escape_string(raw_val)
                                final_val = f'"{safe_str}"'
                            else:
                                final_val = raw_val
                            self.header_manager.add_global(f"{g_type} {name} = {final_val};")

                # --- 3. 解析 FUNC (内部函数标识) ---
                elif cat == 'FUNC':
                    try:
                        g_id_str = row.get('Global_ID', '').lstrip('\t')
                        if not g_id_str.isdigit():
                            raise ValueError(f"Invalid or missing Global_ID: '{g_id_str}'")

                        global_id = int(g_id_str)
                        self.func_map[global_id] = name

                        if name not in self.func_params:
                            self.func_params[name] = []
                        if name not in self.func_locals:
                            self.func_locals[name] = []
                    except Exception as e:
                        logger.error_and_stop(f"[LGC-CONTEXT] FUNC parse error at row {row_idx} ({name}): {e}")

                # --- 4. 解析 PARAM (函数参数) ---
                elif cat == 'PARAM':
                    if '_arg' not in name:
                        logger.error_and_stop(f"[LGC-CONTEXT] PARAM format error at row {row_idx} ({name}): Missing '_arg' separator.")
                        continue

                    func_part = name.split('_arg')[0]
                    p_type = row.get('Type', 'int').lstrip('\t')

                    decl = f"{p_type} {name}"
                    if is_init and raw_val not in ('N/A', ''):
                        if p_type == 'string':
                            safe_str = self._escape_string(raw_val)
                            decl += f' = "{safe_str}"'
                        else:
                            decl += f" = {raw_val}"

                    if func_part not in self.func_params:
                        logger.error_and_stop(
                            f"[LGC-CONTEXT] PARAM '{name}' mapped to unknown function '{func_part}' at row {row_idx}. Auto-registering.")
                        self.func_params[func_part] = []
                    self.func_params[func_part].append(decl)

                # --- 5. 解析 LOCAL_VAR (局部变量) ---
                elif cat == 'LOCAL_VAR':
                    if '@' not in name:
                        logger.error_and_stop(f"[LGC-CONTEXT] LOCAL_VAR format error at row {row_idx} ({name}): Missing '@' separator.")
                        continue

                    func_part = name.split('@')[0]
                    local_name = name.replace('@', '_')
                    l_type = row.get('Type', 'int').lstrip('\t')

                    decl = ""
                    if is_array:
                        if is_init and raw_val not in ('N/A', ''):
                            try:
                                val_list = json.loads(raw_val)
                                formatted_vals = []
                                for v in val_list:
                                    if l_type == 'string':
                                        safe_str = self._escape_string(v)
                                        formatted_vals.append(f'"{safe_str}"')
                                    else:
                                        formatted_vals.append(str(v))

                                init_str = ', '.join(formatted_vals)
                                decl = f"static {l_type} {local_name}[{size_str}] = {{ {init_str} }};"
                            except json.JSONDecodeError as e:
                                logger.error_and_stop(f"[LGC-CONTEXT] LOCAL_VAR array JSON decode error at row {row_idx} ({name}): {e}")
                                decl = f"static {l_type} {local_name}[{size_str}]; // Parse Init failed"
                        else:
                            decl = f"static {l_type} {local_name}[{size_str}];"
                    else:
                        if is_init and raw_val not in ('N/A', ''):
                            if l_type == 'string' and not raw_val.startswith('"'):
                                safe_str = self._escape_string(raw_val)
                                final_val = f'"{safe_str}"'
                            else:
                                final_val = raw_val
                            decl = f"static {l_type} {local_name} = {final_val};"
                        else:
                            decl = f"{l_type} {local_name};"

                    if func_part not in self.func_locals:
                        self._report_error(
                            f"[LGC-CONTEXT] LOCAL_VAR '{name}' mapped to unknown function '{func_part}' at row {row_idx}. Auto-registering.")
                        self.func_locals[func_part] = []
                    self.func_locals[func_part].append(decl)

        # 在所有的 CSV 行解析完毕后，集中生成 EXTERN 文件头
        # 此时已经拿到了所有的 PARAM 参数（如果有），带上了初始值
        for ext_id, (name, size_int) in self.ext_map.items():
            params = self.func_params.get(name, [])
            self.header_manager.add_extern(f"extern {name}({', '.join(params)}) {ext_id};")