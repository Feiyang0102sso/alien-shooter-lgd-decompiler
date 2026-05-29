"""
test_segment_merger.py

针对 LGC 拆分器中普通代码段（Segment）哈希去重比对、防撞名避让以及多文件引用序列生成的单元测试。
"""

import pytest
from pathlib import Path
from lgd_tool.lgd_decompiler.LGC_splitter import (
    LgcFunction,
    LgcSegmentPool,
    merge_decompiled_project,
)


def test_segment_pool_match_and_deduplication(tmp_path: Path) -> None:
    """
    测试 1：两关切分出的代码段内容完全一模一样（差一个字节都不行）时：
    1. 它们应当在全局哈希池中被合并去重，物理磁盘上仅写出唯一的 segment_00.lgc 物理文件。
    2. 两关在 file_references 中对应的物理文件名引用序列，都应成功且有序地指向同一个 "segment_00.lgc"！
    """
    pool = LgcSegmentPool(tmp_path)

    # 1. 模拟第一关的普通段
    func_a = LgcFunction(
        name="funcA",
        start_line_idx=10,
        lines=[
            "funcA()",
            "{",
            "    int x = 1;",
            "}"
        ]
    )
    seg_00_level1 = [func_a]

    # 2. 模拟第二关的普通段，在字符上与第一关完完全全 100% 相同
    func_a_identical = LgcFunction(
        name="funcA",
        start_line_idx=20,
        lines=[
            "funcA()",
            "{",
            "    int x = 1;",
            "}"
        ]
    )
    seg_00_level2 = [func_a_identical]

    # 3. 注册两关的数据
    pool.register_file_segments("level_01.lgc", [seg_00_level1])
    pool.register_file_segments("level_02.lgc", [seg_00_level2])

    # 4. 验证合并结果
    # 4.1 物理上仅生成了 segment_00.lgc
    assert (tmp_path / "segment_00.lgc").exists()
    assert not (tmp_path / "segment_01.lgc").exists()

    # 4.2 两关的物理引用顺序列表均准确且有序指向同一个 "segment_00.lgc"
    assert pool.file_references["level_01.lgc"] == ["segment_00.lgc"]
    assert pool.file_references["level_02.lgc"] == ["segment_00.lgc"]


def test_segment_pool_different_by_one_space(tmp_path: Path) -> None:
    """
    测试 2：两关切分出的代码段仅相差一个空格时：
    根据“差一个字节都不行”的严苛规则，它们的哈希必定不同，判定为不同段，物理生成各自独立的物理文件。
    """
    pool = LgcSegmentPool(tmp_path)

    func_a = LgcFunction(
        name="funcA",
        start_line_idx=10,
        lines=[
            "funcA()",
            "{",
            "    int x = 1;",
            "}"
        ]
    )

    # 尾部故意多出一个排版空格，字节不同
    func_a_with_space = LgcFunction(
        name="funcA",
        start_line_idx=20,
        lines=[
            "funcA()",
            "{",
            "    int x = 1; ", 
            "}"
        ]
    )

    pool.register_file_segments("level_01.lgc", [[func_a]])
    pool.register_file_segments("level_02.lgc", [[func_a_with_space]])

    # 验证物理上生成了两个独立的代码文件（没有强行去重，从 00 开始分配）
    assert (tmp_path / "segment_00.lgc").exists()
    assert (tmp_path / "segment_01.lgc").exists()


def test_segment_pool_new_and_naming_collisions(tmp_path: Path) -> None:
    """
    测试 3：当不同关卡有多个内容完全不同的新代码段时，以及当名字被意外抢占时：
    1. 两个内容不同新段，应当物理生成各自独立的物理文件（segment_00.lgc 与 segment_01.lgc）。
    2. 当分配的文件名已被 assigned_filenames 占用（物理抢占冲突），防撞名安全阀应能自动递增为 segment_00_001.lgc 保证落盘安全。
    """
    pool = LgcSegmentPool(tmp_path)

    # 1. 模拟段 1 (内容为 funcA)
    func_a = LgcFunction(
        name="funcA",
        start_line_idx=0,
        lines=["funcA() { int x = 1; }"]
    )
    
    # 2. 模拟段 2 (内容不同，为 funcB)
    func_b = LgcFunction(
        name="funcB",
        start_line_idx=0,
        lines=["funcB() { string s = \"hello\"; }"]
    )

    # 3. 人为强行占用文件名 "segment_00.lgc"，模拟严重的抢占命名冲突
    pool.assigned_filenames.add("segment_00.lgc")

    # 4. 注册不同新段
    pool.register_file_segments("level_01.lgc", [[func_a]])
    pool.register_file_segments("level_02.lgc", [[func_b]])

    # 5. 验证命名避让机制是否成功触发
    # 5.1 第一个本该分配 segment_00.lgc 的新段，由于被我们人为抢占，安全避让为生成 segment_00_001.lgc！
    assert (tmp_path / "segment_00_001.lgc").exists()
    assert pool.file_references["level_01.lgc"] == ["segment_00_001.lgc"]

    # 5.2 第二个段顺利以 segment_01.lgc 分配落盘！
    assert (tmp_path / "segment_01.lgc").exists()
    assert pool.file_references["level_02.lgc"] == ["segment_01.lgc"]


def test_merge_decompiled_project_pipeline(tmp_path: Path) -> None:
    """
    测试 4：全项目一键统一合并（Pipeline）的集成测试：
    1. 验证 Export 强一致校验通过并写盘。
    2. 验证 Global 无冲突合流写盘、冲突变量在主入口中被注入。
    3. 验证普通段哈希匹配去重，物理只写出一份普通段。
    4. 验证各大文件的主入口脚本头部被成功拼接入包含公共和段依赖的 #include 链。
    """
    # 模拟项目提取数据
    project_data = {
        "level_01.lgc": {
            "exports": [
                "extern stackObject(int arg0) 100;",
                "extern setAmbient(string music) 200;"
            ],
            "globals": [
                "int SoundVolume;",
                "int StartTeleport = 0;" # 冲突：此文件为 0
            ],
            "segments": [
                [
                    LgcFunction(name="funcA", start_line_idx=0, lines=["funcA() { int x = 1; }"])
                ]
            ],
            "last_segment_lines": [
                "func_level_01_main() { }"
            ]
        },
        "level_02.lgc": {
            "exports": [
                "extern stackObject(int arg0) 100;",
                "extern setAmbient(string music) 200;"
            ],
            "globals": [
                "int SoundVolume;",
                "int StartTeleport = 1;" # 冲突：此文件为 1
            ],
            "segments": [
                [
                    # 哈希相同，应去重合并！
                    LgcFunction(name="funcA", start_line_idx=0, lines=["funcA() { int x = 1; }"])
                ]
            ],
            "last_segment_lines": [
                "func_level_02_main() { }"
            ]
        }
    }

    # 执行一键反编译项目比对合并与落盘
    file_references = merge_decompiled_project(
        project_data=project_data,
        output_dir=tmp_path
    )

    # 1. 验证公共 Export 写盘
    public_export = tmp_path / "core" / "export.lgc"
    assert public_export.exists()
    assert "extern stackObject(int arg0) 100;" in public_export.read_text(encoding="utf-8")

    # 2. 验证公共 Global 写盘
    public_global = tmp_path / "core" / "global_variable.lgc"
    assert public_global.exists()
    assert "int SoundVolume;" in public_global.read_text(encoding="utf-8")
    assert "StartTeleport" not in public_global.read_text(encoding="utf-8") # 冲突的被剔除

    # 3. 验证普通段去重合并
    # 两关依赖同一个普通段，物理上仅写出一份 segment_00.lgc
    seg_file = tmp_path / "segment_00.lgc"
    assert seg_file.exists()
    assert not (tmp_path / "segment_01.lgc").exists()
    assert file_references["level_01.lgc"] == ["segment_00.lgc"]
    assert file_references["level_02.lgc"] == ["segment_00.lgc"]

    # 验证普通段头部是否已经成功引入了 core/export 以及 core/global_variable
    seg_content = seg_file.read_text(encoding="utf-8")
    assert '#include "core\\export.lgc"' in seg_content
    assert '#include "core\\global_variable.lgc"' in seg_content

    # 4. 验证最终物理主入口脚本（level_01.lgc 与 level_02.lgc）是否被成功拼装
    main_01 = tmp_path / "level_01.lgc"
    assert main_01.exists()
    content_01 = main_01.read_text(encoding="utf-8")
    # 验证头部依赖 include 链顺利拼合
    assert '#include "core\\export.lgc"' in content_01
    assert '#include "core\\global_variable.lgc"' in content_01
    assert '#include "segment_00.lgc"' in content_01
    # 验证注入了特异冲突变量 StartTeleport = 0，且注入位置必须在普通段 segment_00.lgc 被 include 之前！
    assert 'int StartTeleport = 0;' in content_01
    idx_decl_01 = content_01.index('int StartTeleport = 0;')
    idx_inc_01 = content_01.index('#include "segment_00.lgc"')
    assert idx_decl_01 < idx_inc_01

    # 验证尾段拼接了原有主入口函数
    assert 'func_level_01_main() { }' in content_01

    main_02 = tmp_path / "level_02.lgc"
    assert main_02.exists()
    content_02 = main_02.read_text(encoding="utf-8")
    assert '#include "core\\export.lgc"' in content_02
    assert '#include "core\\global_variable.lgc"' in content_02
    assert '#include "segment_00.lgc"' in content_02

    # 同理校验第二关中特异冲突变量 StartTeleport = 1 的顺序
    assert 'int StartTeleport = 1;' in content_02
    idx_decl_02 = content_02.index('int StartTeleport = 1;')
    idx_inc_02 = content_02.index('#include "segment_00.lgc"')
    assert idx_decl_02 < idx_inc_02

    assert 'func_level_02_main() { }' in content_02
