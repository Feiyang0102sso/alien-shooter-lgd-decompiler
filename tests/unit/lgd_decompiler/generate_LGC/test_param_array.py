"""
tests/unit/lgd_decompiler/generate_LGC/test_param_array.py
测试 LgcContext 解析带有数组参数的 PARAM 类别。
"""

import pytest
from pathlib import Path
from lgd_tool.lgd_decompiler.generate_LGC.lgc_context import LgcContext


def test_param_array_parsing(tmp_path: Path):
    """
    测试 LgcContext 能正确解析 CSV 中的参数数组并包含其大小尺寸。
    """
    # 准备测试 CSV 临时路径
    csv_file = tmp_path / "test_param_array.csv"

    # 写入包含数组类型 PARAM 的 CSV 测试数据
    csv_content = (
        "Global_ID,P1_Index,File_ID,Name,Category,Type,Is_Array,Size,Is_Initialized,Init_Value,Extern_ID,Param_Types\n"
        '3202,20086,0,setIntoxicationDamagePerSecond_arg0,PARAM,int,True,10,False,N/A,N/A,N/A\n'
    )
    csv_file.write_text(csv_content, encoding="utf-8")

    # 初始化 LgcContext 并载入该 CSV
    context = LgcContext()
    context.load_from_csv(str(csv_file))

    # 验证函数名 setIntoxicationDamagePerSecond 关联的参数列表
    params = context.func_params.get("setIntoxicationDamagePerSecond")

    # 断言列表不为空且解析出的第一个参数包含正确大小的数组后缀
    assert params is not None
    assert len(params) == 1
    assert params[0] == "int setIntoxicationDamagePerSecond_arg0[10]"
