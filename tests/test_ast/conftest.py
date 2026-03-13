# test/test_ast/conftest.py
import pytest
from pathlib import Path
from .test_ast_util import parse_asm_methods, build_ast_for_method

# 定义数据文件路径
DATA_DIR = Path(__file__).parent / "data"
ASM_FILE = DATA_DIR / "test_stack_in_ifdef.lgd.asm"


def _get_all_methods():
    if not ASM_FILE.exists():
        return []
    return parse_asm_methods(str(ASM_FILE))


# 提前解析出所有的 methods
METHODS = _get_all_methods()
METHOD_NAMES = [m.name for m in METHODS]


@pytest.fixture(scope="session", params=METHODS, ids=METHOD_NAMES)
def ast_method_session(request):
    """
    这个 fixture 会自动为 ASM 文件中的每一个 Method 运行一次测试！
    每次提供 (method_name, statements) 元组。
    """
    method = request.param

    # 针对当前传入的方法生成 AST
    statements = build_ast_for_method(method)

    # 交给测试用例
    yield method.name, statements