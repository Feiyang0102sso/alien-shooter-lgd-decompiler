# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

# === Dynamic Version Generation ===
spec_dir = Path(SPECPATH)


version_file = spec_dir / 'src' / 'lgd_tool' / 'version.py'
v_env = {}
exec(version_file.read_text(encoding='utf-8'), v_env)

version_str = v_env.get('__version__', '0.0.0')
# e.g '0.3.0' -> (0, 3, 0, 0)
v_tuple = tuple(map(int, (version_str + ".0.0").split('.')))[:4]
v_tuple_str = f"({v_tuple[0]}, {v_tuple[1]}, {v_tuple[2]}, {v_tuple[3]})"

version_info_content = f"""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={v_tuple_str},
    prodvers={v_tuple_str},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'040904B0',
        [
        StringStruct(u'CompanyName', u'Feiyang'),
        StringStruct(u'FileDescription', u'LGD Decompiler'),
        StringStruct(u'FileVersion', u'{version_str}'),
        StringStruct(u'InternalName', u'LgdDecompiler'),
        StringStruct(u'LegalCopyright', u'© 2026 Feiyang All rights reserved.'),
        StringStruct(u'OriginalFilename', u'LgdDecompiler.exe'),
        StringStruct(u'ProductName', u'LGD Decompiler'),
        StringStruct(u'ProductVersion', u'{version_str}')])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
"""

dyn_version_file = spec_dir / 'version_info_dynamic.txt'
dyn_version_file.write_text(version_info_content, encoding='utf-8')
# ==================================

a = Analysis(
    ['launcher.py'],
    pathex=['src'],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['test', '.lgd_sample', 'pytest', 'unittest', 'scripts'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='LgdDecompiler',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,

    icon='assets/logo.ico',
    # 注意：PyInstaller 内部有些老代码只认字符串路径，所以这里安全起见套个 str()
    version=str(dyn_version_file)
)

# === Cleanup after build ===
try:
    dyn_version_file.unlink(missing_ok=True)
except Exception:
    pass

# pyinstaller LgdDecompiler.spec --clean
# .\.venv\Scripts\Activate.ps1