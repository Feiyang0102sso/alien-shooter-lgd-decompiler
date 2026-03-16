"""
tests/test_optimizer/conftest.py
为 test_optimizer 测试集定义 session 级别的 fixture。
自动扫描 data 目录下的驱动文件并进行流水线测试。
"""
import pytest
from pathlib import Path

from .test_optimizer_util import generate_and_read_lgc

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"

# 动态获取所有以 .lgd.asm 结尾的文件
ASM_FILES = list(DATA_DIR.glob("*.lgd.asm"))
ASM_NAMES = [p.name for p in ASM_FILES]


@pytest.fixture(scope="session", params=ASM_FILES, ids=ASM_NAMES)
def lgc_session(request):
    """
    对每个抓取到的 ASM 文件，运行一次流水线生成 LGC，
    并将生成的内容和文件名交出供测试使用。
    """
    asm_path = request.param

    # 根据 asm 文件名动态推导 csv 和目标输出 lgc 的路径
    # 例如 test_loc_unstatic_arr.lgd.asm -> test_loc_unstatic_arr.lgd.csv
    base_name = asm_path.stem  # test_loc_unstatic_arr.lgd
    csv_path = asm_path.with_name(f"{base_name}.csv")

    # 构造输出文件名 (替换后缀)
    prefix = asm_path.name.split('.')[0]
    output_lgc_path = DATA_DIR / f"{prefix}_output.lgc"

    # Setup: 运行生成流水线并读取
    content = generate_and_read_lgc(asm_path, csv_path, output_lgc_path)

    # 交给后续具体的测试用例
    yield content, asm_path.name

    # Teardown: 自动清理生成的 LGC 产物
    if output_lgc_path.exists():
        output_lgc_path.unlink()