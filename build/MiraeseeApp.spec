# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec — onedir + bootloader splash (assets ship beside exe).
# Build: pyinstaller build/MiraeseeApp.spec

import sys
from pathlib import Path

from PyInstaller.building.splash import Splash

project_dir = Path(SPECPATH).resolve().parent
sys.path.insert(0, str(project_dir / "build"))
from bundle_prune import collect_app_datas, prune_analysis

splash_img = project_dir / "assets" / "icon.png"

a = Analysis(
	[str(project_dir / "main.py")],
	pathex=[str(project_dir)],
	binaries=[],
	datas=collect_app_datas(project_dir),
	hiddenimports=[
		"PySide6.QtQuick",
		"PySide6.QtQml",
		"PySide6.QtGui",
		"PySide6.QtCore",
	],
	hookspath=[],
	hooksconfig={},
	runtime_hooks=[],
	excludes=[
		"pytest",
		"IPython",
		"tkinter",
		"matplotlib",
		"numpy",
		"pandas",
		"scipy",
		"PIL",
		"cv2",
		"pygame",
		"jupyter",
		"notebook",
		"setuptools",
		"pip",
		"wheel",
		"unittest",
		"test",
		"lib2to3",
		"pydoc",
		"doctest",
		"xmlrpc",
		"curses",
		"readline",
		"bdb",
		"pdb",
		"wmi",
		"PySide6.QtWidgets",
		"PySide6.QtWebEngineCore",
		"PySide6.QtWebEngineWidgets",
		"PySide6.QtWebEngineQuick",
		"PySide6.QtPdf",
		"PySide6.QtQuick3D",
		"PySide6.Qt3DCore",
		"PySide6.QtCharts",
		"PySide6.QtGraphs",
		"PySide6.QtLocation",
		"PySide6.QtMultimedia",
		"PySide6.QtPositioning",
		"PySide6.QtSensors",
		"PySide6.QtRemoteObjects",
		"PySide6.QtScxml",
		"PySide6.QtTest",
		"PySide6.QtVirtualKeyboard",
		"PySide6.QtBluetooth",
		"PySide6.QtNfc",
		"PySide6.QtSerialPort",
		"PySide6.QtDesigner",
		"PySide6.QtDataVisualization",
		"PySide6.QtWebChannel",
		"PySide6.QtWebView",
		"PySide6.QtSpeech",
		"PySide6.QtStateMachine",
		"PySide6.QtShaderTools",
	],
	noarchive=False,
	optimize=1,
)

prune_analysis(a)

splash = (
	Splash(
		str(splash_img),
		a.binaries,
		a.datas,
		max_img_size=(512, 512),
	)
	if splash_img.is_file()
	else None
)

pyz = PYZ(a.pure)

exe = EXE(
	pyz,
	a.scripts,
	*( [splash] if splash is not None else [] ),
	[],
	name="MiraeseeApp",
	icon=str(project_dir / "assets" / "icon.ico"),
	debug=False,
	bootloader_ignore_signals=False,
	strip=False,
	upx=True,
	upx_exclude=[],
	runtime_tmpdir=None,
	console=False,
	disable_windowed_traceback=False,
	argv_emulation=False,
	target_arch=None,
	codesign_identity=None,
	entitlements_file=None,
	exclude_binaries=True,
)

_coll = [exe, a.binaries, a.datas]
if splash is not None:
	_coll.append(splash.binaries)

coll = COLLECT(
	*_coll,
	strip=False,
	upx=True,
	upx_exclude=[],
	name="MiraeseeApp",
)
