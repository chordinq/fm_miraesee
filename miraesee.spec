# miraesee.spec
# Build: pyinstaller miraesee.spec

import os
from PyInstaller.building.build_main import Analysis, PYZ, EXE, COLLECT

ROOT = os.path.abspath(".")

a = Analysis(
    ["main.py"],
    pathex=[ROOT],
    binaries=[],
    datas=[
        # JSON config files must travel with the exe
        ("configs/parsed_configs",  "configs/parsed_configs"),
        ("configs/localization",    "configs/localization"),
        ("configs/*.json",          "configs"),
        ("assets/Textures",         "assets/Textures"),
    ],
    hiddenimports=[
        "prompt_toolkit",
        "prompt_toolkit.history",
        "prompt_toolkit.auto_suggest",
        "prompt_toolkit.formatted_text",
        "prompt_toolkit.styles",
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="miraesee",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,           # CLI app — keep the console window
    icon="assets/icon/sunglass_inq.ico",
)
