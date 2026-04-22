"""
tests/unit/lgd_decompiler/generate_LGC/test_unstatic_array.py
测试非 static 局部数组的声明和逐元素赋值合并。

直接指定 test_loc_unstatic_arr.lgd.asm 作为数据源，
不依赖全局 lgc_session 的参数化扫描。
"""

import pytest

from tests.conftest import ASM_FILES_DIR
from tests.utils.lgc_helpers import generate_and_read_lgc

# 目标 ASM 文件路径
_ASM_PATH = ASM_FILES_DIR / "test_loc_unstatic_arr.lgd.asm"
_CSV_PATH = ASM_FILES_DIR / "test_loc_unstatic_arr.lgd.csv"
_OUTPUT_LGC_PATH = ASM_FILES_DIR / "test_loc_unstatic_arr_output.lgc"


@pytest.fixture(scope="module")
def generated_lgc_content():
    """运行 LGC 生成流水线，返回生成的 LGC 文本内容。"""
    content = generate_and_read_lgc(_ASM_PATH, _CSV_PATH, _OUTPUT_LGC_PATH)

    yield content

    if _OUTPUT_LGC_PATH.exists():
        _OUTPUT_LGC_PATH.unlink()


class TestUnstaticArrayDeclaration:
    """测试声明区：static 与非 static 数组的区分，以及初始化值合并。"""

    def test_static_initialized_int_array(self, generated_lgc_content):
        """Is_Initialized=True 的 int 数组应保留 static 并带初始值。"""
        assert "static int main_local2[4] = { 1, 2, 3, 4 };" in generated_lgc_content

    def test_static_initialized_string_array(self, generated_lgc_content):
        """Is_Initialized=True 的 string 数组应保留 static 并带初始值。"""
        assert 'static string main_local32[3] = { "111", "222", "333" };' in generated_lgc_content

    def test_unstatic_no_init_value_int(self, generated_lgc_content):
        """Is_Initialized=False 且无赋值的 int 数组不应有 static。"""
        assert "    int main_local6[10];" in generated_lgc_content
        assert "static int main_local6[10]" not in generated_lgc_content

    def test_unstatic_no_init_value_string(self, generated_lgc_content):
        """Is_Initialized=False 且无赋值的 string 数组不应有 static。"""
        assert "    string main_local35[10];" in generated_lgc_content
        assert "static string main_local35" not in generated_lgc_content

    def test_unstatic_int_array_with_init_in_decl(self, generated_lgc_content):
        """非 static int 数组的初始化值应合并到声明区。"""
        assert "    int main_local16[6] = { 1, 2, 3, 4, 5, 6 };" in generated_lgc_content
        assert "    int main_local22[10] = { 1, 2, 3, 4, 5, 6 };" in generated_lgc_content

    def test_unstatic_string_array_with_init_in_decl(self, generated_lgc_content):
        """非 static string 数组的初始化值应合并到声明区。"""
        assert '    string main_local45[3] = { "111", "222", "333" };' in generated_lgc_content

    def test_no_false_static_on_unstatic_arrays(self, generated_lgc_content):
        """确保非 static 数组声明中不出现 static 关键字。"""
        assert "static int main_local16" not in generated_lgc_content
        assert "static int main_local22" not in generated_lgc_content
        assert "static string main_local45" not in generated_lgc_content
        assert "static string main_local48" not in generated_lgc_content

    def test_no_empty_unstatic_when_has_init(self, generated_lgc_content):
        """有初始化的非 static 数组声明不应出现无初始化版本。"""
        lines = generated_lgc_content.split("\n")
        for line in lines:
            if line.strip() == "int main_local16[6];":
                pytest.fail("Found un-initialized declaration for main_local16")


class TestArrayElementMerge:
    """测试函数体：逐元素赋值已从函数体中移除。"""

    def test_no_individual_element_assigns(self, generated_lgc_content):
        """合并后，函数体中不应再出现逐元素赋值。"""
        assert "main_local16 = 1;" not in generated_lgc_content
        assert "main_local17 = 2;" not in generated_lgc_content
        assert "main_local21 = 6;" not in generated_lgc_content
        assert "main_local22 = 1;" not in generated_lgc_content
        assert "main_local27 = 6;" not in generated_lgc_content
        assert 'main_local45 = "111";' not in generated_lgc_content
        assert 'main_local46 = "222";' not in generated_lgc_content
        assert 'main_local47 = "333";' not in generated_lgc_content

    def test_no_body_array_assign(self, generated_lgc_content):
        """函数体中不应出现 arrayName = { ... } 形式的赋值。"""
        assert "main_local16 = {" not in generated_lgc_content
        assert "main_local22 = {" not in generated_lgc_content
        assert "main_local45 = {" not in generated_lgc_content

    def test_line_comments_deduplicated(self, generated_lgc_content):
        """重复的 line 注释应已去重。"""
        lines = generated_lgc_content.split("\n")
        stripped_lines = [line.strip() for line in lines]
        for i in range(len(stripped_lines) - 1):
            if stripped_lines[i].startswith("// --- Line") and stripped_lines[i].endswith("---"):
                assert stripped_lines[i] != stripped_lines[i + 1], \
                    f"Found duplicate consecutive line comment: {stripped_lines[i]}"

    def test_static_scalar_unchanged(self, generated_lgc_content):
        """static 标量变量不受影响。"""
        assert "static int main_local1 = 100;" in generated_lgc_content

    def test_normal_scalar_unchanged(self, generated_lgc_content):
        """普通标量赋值不受影响。"""
        assert "int main_local0;" in generated_lgc_content
        assert "main_local0 = 100;" in generated_lgc_content
