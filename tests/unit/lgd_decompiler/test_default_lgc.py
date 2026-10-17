"""
tests/unit/lgd_decompiler/test_default_lgc.py
测试 main.py 中为缺少脚本的地图文件夹补空 default.lgc 的逻辑。
"""

from pathlib import Path

from lgd_tool.main import create_missing_default_lgc


def _touch(path: Path, content: str = "") -> None:
    """创建文件及其父目录。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def test_create_default_for_maps_without_script(tmp_path: Path):
    """
    模拟 ASNE addon0/lobby：只有 .map 没有任何 .lgc，应补一个空 default.lgc。
    """
    _touch(tmp_path / "addon0" / "lobby" / "lobby_01.map")
    _touch(tmp_path / "addon0" / "lobby" / "lobby_02.map")

    created = create_missing_default_lgc(tmp_path)

    default_lgc = tmp_path / "addon0" / "lobby" / "default.lgc"
    assert created == [default_lgc]
    assert default_lgc.read_text(encoding="utf-8") == ""


def test_skip_when_default_exists(tmp_path: Path):
    """
    已有 default.lgc 时不得覆盖。
    """
    _touch(tmp_path / "addon0" / "level_01.map")
    _touch(tmp_path / "addon0" / "default.lgc", "keep me")

    created = create_missing_default_lgc(tmp_path)

    assert created == []
    assert (tmp_path / "addon0" / "default.lgc").read_text(encoding="utf-8") == "keep me"


def test_skip_when_every_map_has_own_script(tmp_path: Path):
    """
    每个 .map 都有同名 .lgc 时无需补 default.lgc。
    """
    _touch(tmp_path / "main.map")
    _touch(tmp_path / "main.lgc", "main()")
    _touch(tmp_path / "logo.map")
    _touch(tmp_path / "logo.lgc", "main()")

    created = create_missing_default_lgc(tmp_path)

    assert created == []
    assert (tmp_path / "default.lgc").exists() is False


def test_no_fallback_when_folder_has_any_lgc(tmp_path: Path):
    """
    文件夹内已有任何 .lgc 时不兜底：即便部分 .map 缺脚本，也交给编译器报错暴露问题。
    """
    _touch(tmp_path / "survive" / "survive_01.map")
    _touch(tmp_path / "survive" / "survive_01.lgc", "main()")
    _touch(tmp_path / "survive" / "survive_02.map")

    created = create_missing_default_lgc(tmp_path)

    assert created == []
    assert (tmp_path / "survive" / "default.lgc").exists() is False
