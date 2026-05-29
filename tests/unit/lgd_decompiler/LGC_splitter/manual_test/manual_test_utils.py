"""
manual_test_utils.py
"""
import shutil
from pathlib import Path

_CURRENT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _CURRENT_DIR.parents[4]

def load_tutorial_lgc_content() -> str | None:
    """
    读取默认的 regression_tutorial_00.lgc 文件内容。
    调用: content = load_tutorial_lgc_content()
    """

    print(f"root: {_CURRENT_DIR}")

    lgc_file_path = (
        _PROJECT_ROOT
        / "tests"
        / "fixtures"
        / "regression_lgc"
        / "regression_tutorial_00.lgc"
    )

    if not lgc_file_path.exists():
        print(f"[错误] 未找到真实的测试文件: {lgc_file_path}")
        return None  # 明确返回 None

    print("=" * 70)
    print(f"正在读取真实 LGC 文件: {lgc_file_path.name} ({lgc_file_path.stat().st_size / 1024:.1f} KB)")
    print("=" * 70)

    # 读取内容并返回
    return lgc_file_path.read_text(encoding="utf-8", errors="replace")


def setup_temp_dir(dir_name: str = "_manual_test_temp", base_dir: Path = _CURRENT_DIR) -> Path:
    """
    创建一个干净的临时目录。
    """
    temp_dir = base_dir / dir_name

    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    temp_dir.mkdir(parents=True, exist_ok=True)
    print(f"temp dir: {temp_dir}")
    return temp_dir


def wait_and_cleanup_tmp_dir(target_dir: Path, custom_prompt: str = None) -> None:
    """
    阻塞程序等待用户审查，按下回车后清理目标目录。
    """
    if not target_dir.exists():
        return

    # 如果没有提供自定义提示，就使用默认提示
    prompt_msg = custom_prompt or f"\n>>> 【审查完毕后，请按 Enter 键清空临时目录 {target_dir.name} 并退出】 <<< "

    try:
        input(prompt_msg)
    except KeyboardInterrupt:
        pass

    print(f"\n正在清理临时目录 [{target_dir.name}]...")
    try:
        shutil.rmtree(target_dir)
        print("-> 临时目录已彻底清理干净。")
    except Exception as e:
        print(f"[警告] 清理目录时发生错误: {e}")
