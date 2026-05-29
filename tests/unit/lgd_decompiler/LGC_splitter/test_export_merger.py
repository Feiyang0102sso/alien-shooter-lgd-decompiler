"""
test_export_merger.py

针对 LGC 拆分器中 Export 合并比对与物理原序一致性强校验模块的自动化单元测试。
"""

import pytest
from lgd_tool.lgd_decompiler.LGC_splitter import (
    normalize_declaration_line,
    verify_exports_strictly_identical,
)


def test_normalize_declaration_line() -> None:
    """
    测试声明行的宽容归一化处理。
    去除首尾多余空白，并将行内部多余的连续空格压缩为单个空格。
    """
    input_line = "  extern   stackObject(int    arg0)   100;  "
    expected = "extern stackObject(int arg0) 100;"
    assert normalize_declaration_line(input_line) == expected


def test_verify_exports_identical() -> None:
    """
    测试多个大文件提取出来的 Export 完全一致时，能够成功通过校验并原序返回。
    """
    # 模拟两个文件的 export 列表，内部有不同空格排版，但内容及原物理顺序完全相同
    file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "  extern setAmbient(string music) 200;  ",
            "extern finishResourcesLoad() 255;",
        ],
        "level_02.lgc": [
            "extern   stackObject(int arg0) 100;",
            "extern setAmbient(string   music) 200;",
            "extern finishResourcesLoad()   255;",
        ],
    }

    result = verify_exports_strictly_identical(file_data)

    # 1. 验证数量一致
    assert len(result) == 3
    
    # 2. 验证内容被归一化且物理原序完整返回
    assert result[0] == "extern stackObject(int arg0) 100;"
    assert result[1] == "extern setAmbient(string music) 200;"
    assert result[2] == "extern finishResourcesLoad() 255;"


def test_verify_exports_different_length() -> None:
    """
    测试当有文件提取出来的 export 条目总数不一致时，
    verify_exports_strictly_identical 是否能强制终止进程（即抛出 SystemExit 异常且码为 1）。
    """
    file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
        ],
        "level_02.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
            "extern finishResourcesLoad() 255;", # 多出了一条
        ],
    }

    # 使用 pytest 断言它一定会调用 sys.exit 并抛出 SystemExit
    with pytest.raises(SystemExit) as exc_info:
        verify_exports_strictly_identical(file_data)

    # 验证进程退出状态码为 1
    assert exc_info.value.code == 1


def test_verify_exports_different_content() -> None:
    """
    测试当两个文件的 export 数量相同，但其中某一行的声明内容存在差异时，
    是否能够被成功拦截并强行终止进程。
    """
    file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;", # 基准为 200
        ],
        "level_02.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 201;", # 存在一字节差异 201
        ],
    }

    with pytest.raises(SystemExit) as exc_info:
        verify_exports_strictly_identical(file_data)

    assert exc_info.value.code == 1


def test_verify_exports_different_order() -> None:
    """
    测试当两个文件的 export 内容集一模一样，但由于我们不进行排序，
    若原始物理行的引用顺序不一致，是否也能被原序校验严苛拦截并强制终止进程。
    """
    file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
        ],
        "level_02.lgc": [
            "extern setAmbient(string music) 200;", # 顺序颠倒了
            "extern stackObject(int arg0) 100;",
        ],
    }

    with pytest.raises(SystemExit) as exc_info:
        verify_exports_strictly_identical(file_data)

    assert exc_info.value.code == 1


def test_verify_exports_single_file() -> None:
    """
    测试只有一个文件作为输入时，直接跳过一致性比对，返回干净的归一化声明行列表。
    """
    file_data = {
        "level_01.lgc": [
            "  extern stackObject(int arg0) 100;  ",
            "", # 包含空行
            "extern setAmbient(string music) 200;",
        ]
    }

    result = verify_exports_strictly_identical(file_data)
    
    assert len(result) == 2
    assert result[0] == "extern stackObject(int arg0) 100;"
    assert result[1] == "extern setAmbient(string music) 200;"


def test_verify_exports_empty() -> None:
    """
    测试空字典输入时，安全返回空列表。
    """
    result = verify_exports_strictly_identical({})
    assert len(result) == 0


def test_verify_exports_with_empty_files() -> None:
    """
    测试当部分大文件的 extern 声明完全为空（0 个声明）时：
    1. 应该能宽容通过一致性校验，直接跳过空文件的比对。
    2. 其他所有非空文件必须与首个非空基准 100% 保持完全一致。
    """
    # 模拟三个文件：level_01 有声明，level_02 全空，level_03 与 level_01 一致
    file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
        ],
        "level_02.lgc": [],  # 全空
        "level_03.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
        ],
    }

    result = verify_exports_strictly_identical(file_data)
    assert len(result) == 2
    assert result[0] == "extern stackObject(int arg0) 100;"
    assert result[1] == "extern setAmbient(string music) 200;"

    # 如果有不为空的 level_03 存在差异，即便有空文件 level_02 存在，依然应当熔断
    bad_file_data = {
        "level_01.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 200;",
        ],
        "level_02.lgc": [],  # 全空
        "level_03.lgc": [
            "extern stackObject(int arg0) 100;",
            "extern setAmbient(string music) 201;",  # 存在冲突
        ],
    }

    with pytest.raises(SystemExit) as exc_info:
        verify_exports_strictly_identical(bad_file_data)
    assert exc_info.value.code == 1

