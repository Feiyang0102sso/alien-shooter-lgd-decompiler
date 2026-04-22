"""
tests/unit/lgd_decompiler/LGC_refiner/test_const_refiner_rules.py
测试常量精炼器的替换规则。

验证 SetVidData/GetVidData 的特殊偏移规则和通用分解规则。
"""

from lgd_tool.lgd_decompiler.LGC_refiner.const_refiner import refine_constants


def test_set_vid_data_prefers_special_offset_rule():
    """SetVidData 应优先使用特殊偏移规则（VID_NO_CHILD + 14）而非通用分解。"""
    lgc_text = "SetVidData(771, 106, 2);"
    const_db = {
        "VID": {
            60: "VID_CHILD",
            46: "VID_SPRITETYPE",
            92: "VID_NO_CHILD"
        },
        "SETVID": {}
    }

    refined = refine_constants(lgc_text, const_db)

    assert "SetVidData(771, VID_NO_CHILD + 14, 2);" in refined
    assert "VID_CHILD + VID_SPRITETYPE" not in refined


def test_get_vid_data_single_match_mode_blocks_generic_decompose():
    """GetVidData 在单匹配模式下应阻止通用分解。"""
    lgc_text = "GetVidData(unit_nvid, 106);"
    const_db = {
        "VID": {
            60: "VID_CHILD",
            46: "VID_SPRITETYPE"
        },
        "SETVID": {}
    }

    refined = refine_constants(lgc_text, const_db)

    assert refined == lgc_text


def test_other_functions_still_allow_generic_decompose():
    """其他函数仍允许通用常量分解。"""
    lgc_text = "SetEnvironment(7);"
    const_db = {
        "ENV": {
            3: "ENV_A",
            4: "ENV_B"
        }
    }

    refined = refine_constants(lgc_text, const_db)

    assert refined == "SetEnvironment(ENV_B + ENV_A);"
