"""
LGC_refiner/extern_refiner.py
扫描 LGC 文本中的 extern 声明，用数据库中的官方签名替换。
匹配规则：id + 参数签名（类型 + 默认值状态）必须完全一致。
"""

import re
from lgd_tool.logger import logger


def refine_externs(lgc_text: str, extern_db: dict) -> str:
    """
    扫描 LGC 中所有 extern 声明，尝试用数据库中的官方声明替换。

    :param lgc_text: 原始 LGC 文本
    :param extern_db: 数据库索引 {extern_id: [entry, ...]}
    :return: 替换后的 LGC 文本
    """
    if not extern_db:
        return lgc_text

    # 匹配 extern 声明: extern FuncName(params) ID;
    pattern = re.compile(r'^(extern\s+\w+\s*\(.*?\)\s+\d+\s*;)', re.MULTILINE)
    matches = pattern.findall(lgc_text)

    if not matches:
        logger.info("[Refiner] No extern declarations found in LGC")
        return lgc_text

    success_count = 0
    failed_list = []

    for original_decl in matches:
        replacement = _try_match_extern(original_decl, extern_db)
        if replacement is not None:
            lgc_text = lgc_text.replace(original_decl, replacement, 1)
            success_count += 1
        else:
            # 从声明中提取函数名用于报告
            name_match = re.match(r'extern\s+(\w+)', original_decl)
            name = name_match.group(1) if name_match else original_decl
            failed_list.append(name)

    total = len(matches)
    logger.info(f"[Refiner] Extern refinement: {success_count}/{total} matched successfully")

    if failed_list:
        failed_names = ", ".join(failed_list)
        logger.warning(f"[Refiner] {len(failed_list)} externs unmatched: [{failed_names}]")

    return lgc_text


def _try_match_extern(decl_str: str, extern_db: dict) -> str | None:
    """
    尝试将一条 extern 声明与数据库匹配。

    :return: 匹配成功返回官方声明字符串，失败返回 None
    """
    # 解析声明: extern Name(params) ID;
    m = re.match(r'extern\s+(\w+)\s*\((.*?)\)\s+(\d+)\s*;', decl_str)
    if not m:
        return None

    func_name = m.group(1)
    params_str = m.group(2).strip()
    ext_id = int(m.group(3))

    # 从声明中提取参数签名
    decl_sig = _extract_param_signature(params_str)

    # 在数据库中查找
    entries = extern_db.get(ext_id, [])
    for entry in entries:
        db_sig = _build_db_param_signature(entry)
        if decl_sig == db_sig:
            official_decl = entry["official_decl"]
            # logger.debug(f"[Refiner] Matched extern: {func_name} (id={ext_id})")
            return official_decl

    return None


def _extract_param_signature(params_str: str) -> list:
    """
    从 LGC 声明的参数字符串中提取签名。
    输入: "int arg0, string arg1, int arg2 = 0"
    输出: [("int", False), ("string", False), ("int", True)]
    每个元素为 (类型, 是否有默认值)
    """
    if not params_str:
        return []

    sig = []
    for param in params_str.split(','):
        param = param.strip()
        if not param:
            continue

        has_default = '=' in param
        # 提取类型（第一个单词）
        parts = param.split()
        param_type = parts[0] if parts else "int"
        sig.append((param_type, has_default))

    return sig


def _build_db_param_signature(entry: dict) -> list:
    """
    从数据库条目的 params 列表构建签名。
    输出格式与 _extract_param_signature 一致: [(type, has_default), ...]
    """
    sig = []
    for p in entry.get("params", []):
        param_type = p.get("type", "int")
        has_default = p.get("default") is not None
        sig.append((param_type, has_default))
    return sig
