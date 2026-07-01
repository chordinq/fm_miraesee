"""PyInstaller bundle pruning — drop unused Qt modules and dev assets."""
from __future__ import annotations

import shutil
from pathlib import Path

ALLOWED_FONTS = frozenset(
	{
		"Baloo-Regular.ttf",
		"NotoSansKR-Bold.otf",
		"NotoSansJP-Bold.otf",
		"NotoSansRU-Bold.ttf",
		"NotoSansTR-Bold.ttf",
	}
)

QT_BINARY_DROP = (
	"Qt6WebEngine",
	"QtWebEngine",
	"Qt6Pdf",
	"Qt6Quick3D",
	"Qt63D",
	"Qt6Graphs",
	"Qt6Charts",
	"Qt6Location",
	"Qt6Multimedia",
	"Qt6SpatialAudio",
	"Qt6Positioning",
	"Qt6Sensors",
	"Qt6RemoteObjects",
	"Qt6Scxml",
	"Qt6Test",
	"Qt6VirtualKeyboard",
	"Qt6HttpServer",
	"Qt6Bluetooth",
	"Qt6Nfc",
	"Qt6SerialPort",
	"Qt6Designer",
	"Qt6DataVisualization",
	"Qt6WebChannel",
	"Qt6WebView",
	"Qt6Speech",
	"Qt6StateMachine",
	"Qt6ShaderTools",
	"Qt6Widgets",
)

QT_QML_DROP = (
	"/QtWebEngine/",
	"/QtQuick3D/",
	"/QtCharts/",
	"/QtGraphs/",
	"/QtLocation/",
	"/QtMultimedia/",
	"/QtPositioning/",
	"/QtSensors/",
	"/QtRemoteObjects/",
	"/QtScxml/",
	"/QtTest/",
	"/QtSpeech/",
	"/QtDataVisualization/",
	"/QtWebChannel/",
	"/QtWebView/",
	"/QtPdf/",
	"/Qt/labs/",
	"/QtQuick/VirtualKeyboard/",
	"/QtQuick/Controls/FluentWinUI3/",
	"/QtQuick/Controls/Imagine/",
	"/QtQuick/Controls/Material/",
	"/QtQuick/Controls/Universal/",
	"/QtQuick/Controls/Windows/",
	"/QtQuick/Controls/macOS/",
	"/QtQuick/Controls/iOS/",
	"/QtQuick/Controls/Android/",
	"/QtQuick/Controls/designer/",
	"/QtQuick/Dialogs/",
	"/QtQuick/Particles/",
	"/QtQuick/Shapes/",
	"/QtQuick/Timeline/",
	"/QtQuick/NativeStyle/",
	"/QtQuick/LocalStorage/",
	"/QtQuick/XmlListModel/",
)

QT_PYD_DROP = (
	"QtWebEngine",
	"QtPdf",
	"QtQuick3D",
	"Qt3D",
	"QtCharts",
	"QtGraphs",
	"QtLocation",
	"QtMultimedia",
	"QtPositioning",
	"QtSensors",
	"QtRemoteObjects",
	"QtScxml",
	"QtTest",
	"QtVirtualKeyboard",
	"QtBluetooth",
	"QtNfc",
	"QtSerialPort",
	"QtDesigner",
	"QtDataVisualization",
	"QtWebChannel",
	"QtWebView",
	"QtSpeech",
	"QtStateMachine",
	"QtShaderTools",
	"QtWidgets",
)


def _norm(path: str) -> str:
	return path.replace("\\", "/")


def _drop_qt_binary(dest: str) -> bool:
	n = _norm(dest)
	if not n.startswith("PySide6/"):
		return False
	if any(token in n for token in QT_BINARY_DROP):
		return True
	if "/qml/" in n and any(token in n for token in QT_QML_DROP):
		return True
	base = Path(n).name
	if base.endswith(".pyd") and any(token in base for token in QT_PYD_DROP):
		return True
	return False


def _skip_asset(rel: Path) -> bool:
	parts = [part.lower() for part in rel.parts]
	if "audios" in parts:
		return True
	if "fonts" in parts and rel.name not in ALLOWED_FONTS:
		return True
	return False


def _skip_ui(rel: Path) -> bool:
	parts = rel.parts
	if "__pycache__" in parts:
		return True
	if rel.suffix == ".pyc":
		return True
	return "test" in parts


def collect_app_datas(project_dir: Path) -> list[tuple[str, str]]:
	datas: list[tuple[str, str]] = []
	config_dir = project_dir / "config"
	if config_dir.is_dir():
		for path in config_dir.rglob("*"):
			if not path.is_file():
				continue
			rel = path.relative_to(project_dir)
			datas.append((str(path), str(rel.parent)))
	ui_dir = project_dir / "ui"
	if ui_dir.is_dir():
		for path in ui_dir.rglob("*"):
			if not path.is_file():
				continue
			rel = path.relative_to(project_dir)
			if _skip_ui(rel):
				continue
			datas.append((str(path), str(rel.parent)))
	return datas


def copy_release_assets(project_dir: Path, dest_assets_dir: Path) -> None:
	src_assets = project_dir / "assets"
	if not src_assets.is_dir():
		return
	dest_assets_dir.mkdir(parents=True, exist_ok=True)
	for path in src_assets.rglob("*"):
		if not path.is_file():
			continue
		rel = path.relative_to(project_dir)
		if _skip_asset(rel):
			continue
		out = dest_assets_dir / path.relative_to(src_assets)
		out.parent.mkdir(parents=True, exist_ok=True)
		shutil.copy2(path, out)


def prune_analysis(analysis) -> None:
	before_b = len(analysis.binaries)
	before_d = len(analysis.datas)
	before_bytes = _entry_bytes(analysis.binaries) + _entry_bytes(analysis.datas)
	analysis.binaries = [
		entry for entry in analysis.binaries if not _drop_qt_binary(entry[0])
	]
	analysis.datas = [entry for entry in analysis.datas if not _drop_qt_binary(entry[0])]
	after_b = len(analysis.binaries)
	after_d = len(analysis.datas)
	after_bytes = _entry_bytes(analysis.binaries) + _entry_bytes(analysis.datas)
	print(
		f"bundle_prune: binaries {before_b} -> {after_b}, "
		f"datas {before_d} -> {after_d}, "
		f"payload {_mb(before_bytes)} -> {_mb(after_bytes)} MB"
	)


def _entry_bytes(entries: list[tuple[str, ...]]) -> int:
	total = 0
	for entry in entries:
		path = Path(entry[1] if len(entry) > 1 else entry[0])
		if path.is_file():
			total += path.stat().st_size
	return total


def _mb(num_bytes: int) -> str:
	return f"{num_bytes / 1e6:.1f}"
