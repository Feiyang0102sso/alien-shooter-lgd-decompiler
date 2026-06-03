"""
test_pipeline.py

针对一键运行 Pipeline 及原地备份接口 run_splitter_pipeline 的单元测试。
"""

import tempfile
import shutil
from pathlib import Path
from lgd_tool.lgd_decompiler.LGC_reorganizer import run_splitter_pipeline


def test_run_splitter_pipeline_single_file():
    """
    测试单大文件模式下的一键 Pipeline 调度。
    确保：
    1. 能够在同级目录下原地创建同名的 .bak.lgc 安全备份文件。
    2. 能将 lgc 切分并输出至与 lgd 同名的子文件夹中。
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. 模拟生成虚拟 .lgd 文件与对应的 .lgc 源码文件
        lgd_file = temp_path / "level_test.lgd"
        lgd_file.write_text("dummy lgd binary", encoding="utf-8")
        
        lgc_file = temp_path / "level_test.lgc"
        lgc_content = (
            "extern int Log(string msg);\n"
            "extern int GetTime();\n\n"
            "// --- Global Variables ---\n"
            "int SoundVolume = 1;\n"
            "int AmmoPrice[11] = { 0 };\n\n"
            "base_export()\n"
            "{\n"
            "    // --- Line 200 ---\n"
            "    Log(\"export_func\");\n"
            "}\n\n"
            "segment_01()\n"
            "{\n"
            "    // --- Line 100 ---\n"
            "    Log(\"seg_1\");\n"
            "}\n\n"
            "main()\n"
            "{\n"
            "    // --- Line 50 ---\n"
            "    segment_01();\n"
            "}\n"
        )
        lgc_file.write_text(lgc_content, encoding="utf-8")
        
        # 2. 调用顶层一键 Pipeline
        run_splitter_pipeline(lgd_file)
        
        # 3. 验证原地安全备份是否生成，且内容完全一致
        bak_file = temp_path / "level_test.bak.lgc"
        assert bak_file.exists()
        assert bak_file.read_text(encoding="utf-8") == lgc_content
        
        # 4. 验证是否直接平铺产出在同级目录下
        output_dir = temp_path
        
        # 验证 core 目录的 export 与 global
        export_file = output_dir / "core" / "export.lgc"
        assert export_file.exists()
        export_text = export_file.read_text(encoding="utf-8")
        assert "extern int Log(string msg);" in export_text
        
        global_file = output_dir / "core" / "global_variable.lgc"
        assert global_file.exists()
        global_text = global_file.read_text(encoding="utf-8")
        assert "int SoundVolume = 1;" in global_text
        
        # 验证段落切分文件（segment_00.lgc 应被正确生成）
        segment_00_file = output_dir / "segment_00.lgc"
        assert segment_00_file.exists()

        # 验证最外层 lgc 主脚本被重写，且包含正确的相对路径 #include
        assert lgc_file.exists()
        outer_text = lgc_file.read_text(encoding="utf-8")
        assert '#include "core\\export.lgc"' in outer_text
        assert '#include "core\\global_variable.lgc"' in outer_text
        assert '#include "segment_01.lgc"' in outer_text
        assert "main()" in outer_text


def test_run_splitter_pipeline_batch_mode():
    """
    测试批量模式下多文件的一键 Pipeline 合流与去重。
    确保：
    1. 每一个反编译成功的 .lgc 文件都在原地生成了各自的 .bak.lgc 备份。
    2. 能在 merged_project 目录下成功生成公共 API 与去重后包含有序依赖 include 的入口文件。
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. 模拟生成两个虚拟关卡的 .lgd 和 .lgc 文件
        lgd_1 = temp_path / "level_01.lgd"
        lgd_1.write_text("lgd1", encoding="utf-8")
        lgc_1 = temp_path / "level_01.lgc"
        lgc_1_content = (
            "extern int Log(string msg);\n\n"
            "// --- Global Variables ---\n"
            "int SoundVolume = 1;\n\n"
            "base_export()\n"
            "{\n"
            "    // --- Line 200 ---\n"
            "    Log(\"export_func\");\n"
            "}\n\n"
            "common_func()\n"
            "{\n"
            "    // --- Line 100 ---\n"
            "    Log(\"hello\");\n"
            "}\n\n"
            "main()\n"
            "{\n"
            "    // --- Line 50 ---\n"
            "    common_func();\n"
            "}\n"
        )
        lgc_1.write_text(lgc_1_content, encoding="utf-8")
        
        lgd_2 = temp_path / "level_02.lgd"
        lgd_2.write_text("lgd2", encoding="utf-8")
        lgc_2 = temp_path / "level_02.lgc"
        lgc_2_content = (
            "extern int Log(string msg);\n\n"
            "// --- Global Variables ---\n"
            "int SoundVolume = 1;\n\n"
            "base_export()\n"
            "{\n"
            "    // --- Line 200 ---\n"
            "    Log(\"export_func\");\n"
            "}\n\n"
            "common_func()\n"
            "{\n"
            "    // --- Line 100 ---\n"
            "    Log(\"hello\");\n"
            "}\n\n"
            "main()\n"
            "{\n"
            "    // --- Line 50 ---\n"
            "    Log(\"level02\");\n"
            "}\n"
        )
        lgc_2.write_text(lgc_2_content, encoding="utf-8")
        
        success_list = [str(lgd_1), str(lgd_2)]
        
        # 2. 调用批量最高层一键 Pipeline
        run_splitter_pipeline(temp_path, success_list=success_list)
        
        # 3. 验证原地安全备份是否生成
        bak_1 = temp_path / "level_01.bak.lgc"
        bak_2 = temp_path / "level_02.bak.lgc"
        assert bak_1.exists()
        assert bak_2.exists()
        assert bak_1.read_text(encoding="utf-8") == lgc_1_content
        assert bak_2.read_text(encoding="utf-8") == lgc_2_content
        
        # 4. 验证直接在输入路径目录下生成合并的工程文件
        # 验证 core 部分
        export_file = temp_path / "core" / "export.lgc"
        assert export_file.exists()
        export_text = export_file.read_text(encoding="utf-8")
        assert "extern int Log(string msg);" in export_text
        assert '#include "segment_00.lgc"' in export_text  # 第 0 份段前置引入且去除了 ..\\ 前缀
        
        global_file = temp_path / "core" / "global_variable.lgc"
        assert global_file.exists()
        assert "int SoundVolume = 1;" in global_file.read_text(encoding="utf-8")
        
        # 验证普通去重段
        common_func_file = temp_path / "segment_00.lgc"
        assert common_func_file.exists()
        
        # 验证地图入口依赖拼合
        l1_entry = temp_path / "level_01.lgc"
        assert l1_entry.exists()
        l1_entry_text = l1_entry.read_text(encoding="utf-8")
        assert '#include "core\\export.lgc"' in l1_entry_text
        assert '#include "core\\global_variable.lgc"' in l1_entry_text
        assert '#include "segment_00.lgc"' not in l1_entry_text  # 已经被剥离


def test_run_splitter_pipeline_deep_directories():
    """
    测试当 .lgd 和反编译生成的 .lgc 文件分布在不同的多级子文件夹（如 addon0/）下时：
    1. 应当原地为子文件夹下的所有 .lgc 创建 .bak.lgc 物理安全备份。
    2. 能正确地在各自的子文件夹下就地写出/覆盖生成最新的主关卡入口文件。
    3. 写入的 #include 链应该自动且智能地带有正确反推的父级相对路径前缀（如 ..\\core\\export.lgc）。
    """
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. 模拟第一关，在根目录下
        lgd_1 = temp_path / "level_01.lgd"
        lgd_1.write_text("lgd1", encoding="utf-8")
        lgc_1 = temp_path / "level_01.lgc"
        lgc_1_content = (
            "extern int Log(string msg);\n\n"
            "// --- Global Variables ---\n"
            "int SoundVolume = 1;\n\n"
            "base_export()\n"
            "{\n"
            "    // --- Line 200 ---\n"
            "    Log(\"export_func\");\n"
            "}\n\n"
            "common_func()\n"
            "{\n"
            "    // --- Line 100 ---\n"
            "    Log(\"hello\");\n"
            "}\n\n"
            "main()\n"
            "{\n"
            "    // --- Line 50 ---\n"
            "    common_func();\n"
            "}\n"
        )
        lgc_1.write_text(lgc_1_content, encoding="utf-8")
        
        # 2. 模拟第二关，在子目录 addon0/ 之下
        addon_dir = temp_path / "addon0"
        addon_dir.mkdir(parents=True, exist_ok=True)
        
        lgd_2 = addon_dir / "level_02.lgd"
        lgd_2.write_text("lgd2", encoding="utf-8")
        lgc_2 = addon_dir / "level_02.lgc"
        lgc_2_content = (
            "extern int Log(string msg);\n\n"
            "// --- Global Variables ---\n"
            "int SoundVolume = 1;\n\n"
            "base_export()\n"
            "{\n"
            "    // --- Line 200 ---\n"
            "    Log(\"export_func\");\n"
            "}\n\n"
            "common_func()\n"
            "{\n"
            "    // --- Line 100 ---\n"
            "    Log(\"hello\");\n"
            "}\n\n"
            "main()\n"
            "{\n"
            "    // --- Line 50 ---\n"
            "    Log(\"level02_deep\");\n"
            "}\n"
        )
        lgc_2.write_text(lgc_2_content, encoding="utf-8")
        
        success_list = [str(lgd_1), str(lgd_2)]
        
        # 3. 调用批量最高层一键 Pipeline，直出根目录
        run_splitter_pipeline(temp_path, success_list=success_list)
        
        # 4. 验证各自原地备份是否生成
        bak_1 = temp_path / "level_01.bak.lgc"
        bak_2 = addon_dir / "level_02.bak.lgc"
        assert bak_1.exists()
        assert bak_2.exists()
        
        # 5. 验证子目录下就地拆分覆盖写出
        l2_entry = addon_dir / "level_02.lgc"
        assert l2_entry.exists()
        
        # 6. 核心验证：子目录主脚本中拼合的 include 不再带有任何 ..\\ 前缀
        l2_entry_text = l2_entry.read_text(encoding="utf-8")
        assert '#include "core\\export.lgc"' in l2_entry_text
        assert '#include "core\\global_variable.lgc"' in l2_entry_text
        assert '#include "segment_00.lgc"' not in l2_entry_text  # 已经被剥离
