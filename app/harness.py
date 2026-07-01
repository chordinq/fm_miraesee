from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QEventLoop, QUrl
from PySide6.QtGui import QGuiApplication, QIcon
from PySide6.QtQml import QQmlApplicationEngine

from utils.paths import assets_dir, bundle_dir, install_dir

SCRIPTS_ROOT = bundle_dir()
UI_DIR = SCRIPTS_ROOT / "ui"
UI_TEST_DIR = UI_DIR / "test"
TEST_LANGUAGE = "en"


def _app_icon_path() -> Path:
	for base in (install_dir(), bundle_dir()):
		candidate = base / "assets" / "icon.ico"
		if candidate.is_file():
			return candidate
	return install_dir() / "assets" / "icon.ico"


APP_ICON_PATH = _app_icon_path()

__all__ = [
	"SCRIPTS_ROOT",
	"UI_DIR",
	"UI_TEST_DIR",
	"TEST_LANGUAGE",
	"bootstrap",
	"create_application",
	"create_qml_engine",
	"register_qml_services",
	"create_app_engine",
	"default_window_size",
	"loading_window_size",
	"centered_window_origin",
	"set_window_context",
	"set_loading_context",
	"load_qml",
	"clear_qml_roots",
	"sync_window_icons",
	"show_loading_screen",
	"close_boot_splash",
	"APP_ICON_PATH",
]


def bootstrap() -> None:
	root = str(SCRIPTS_ROOT)
	if root not in sys.path:
		sys.path.insert(0, root)
	os.environ.setdefault("QML_XHR_ALLOW_FILE_READ", "1")
	os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")


def apply_app_icon(app: QGuiApplication) -> None:
	if APP_ICON_PATH.is_file():
		app.setWindowIcon(QIcon(str(APP_ICON_PATH)))


def sync_window_icons(engine: QQmlApplicationEngine, app: QGuiApplication) -> None:
	icon = app.windowIcon()
	if icon.isNull():
		return
	for root in engine.rootObjects():
		if hasattr(root, "setIcon"):
			root.setIcon(icon)


def create_application() -> QGuiApplication:
	bootstrap()
	from utils.qml_assets import ensure_internal_assets_link

	ensure_internal_assets_link()
	app = QGuiApplication.instance() or QGuiApplication(sys.argv)
	apply_app_icon(app)
	return app


def create_qml_engine() -> QQmlApplicationEngine:
	from utils.qml_assets import ensure_internal_assets_link

	ensure_internal_assets_link()
	engine = QQmlApplicationEngine()
	engine.addImportPath(str(SCRIPTS_ROOT))
	return engine


def register_qml_services(engine: QQmlApplicationEngine) -> None:
	from ui.utils.localizer import register_loc_manager
	from ui.utils.ui_settings import register_ui_settings
	from controllers.common.number_display_bridge import register_number_display
	from ui.utils.egg_icon_helper import register_egg_icon_helper
	from ui.utils.mount_icon_helper import register_mount_icon_helper
	from ui.utils.pet_icon_helper import register_pet_icon_helper
	from ui.utils.skill_icon_helper import register_skill_icon_helper
	from ui.utils.tech_tree_icon_helper import register_tech_tree_icon_helper

	register_loc_manager(engine)
	register_ui_settings(engine)
	register_number_display(engine)
	register_pet_icon_helper(engine)
	register_egg_icon_helper(engine)
	register_skill_icon_helper(engine)
	register_mount_icon_helper(engine)
	register_tech_tree_icon_helper(engine)


def create_app_engine() -> tuple[QGuiApplication, QQmlApplicationEngine]:
	app = create_application()
	engine = create_qml_engine()
	register_qml_services(engine)
	return app, engine


def _screen_geometry(app: QGuiApplication):
	return app.primaryScreen().availableGeometry()


def window_size(
	app: QGuiApplication,
	width_ratio: float,
	height_ratio: float,
) -> tuple[int, int]:
	geo = _screen_geometry(app)
	return int(geo.width() * width_ratio), int(geo.height() * height_ratio)


def centered_window_origin(
	app: QGuiApplication,
	width: int,
	height: int,
) -> tuple[int, int]:
	geo = _screen_geometry(app)
	x = geo.x() + (geo.width() - width) // 2
	y = geo.y() + (geo.height() - height) // 2
	return x, y


def default_window_size(
	app: QGuiApplication,
	width_ratio: float = 0.9,
	height_ratio: float = 0.9,
) -> tuple[int, int]:
	return window_size(app, width_ratio, height_ratio)


def loading_window_size(app: QGuiApplication) -> tuple[int, int]:
	return window_size(app, 1 / 3, 1 / 3)


def set_loading_context(
	engine: QQmlApplicationEngine,
	app: QGuiApplication,
) -> None:
	width, height = loading_window_size(app)
	x, y = centered_window_origin(app, width, height)
	ctx = engine.rootContext()
	ctx.setContextProperty("loadingWinWidth", width)
	ctx.setContextProperty("loadingWinHeight", height)
	ctx.setContextProperty("loadingWinX", x)
	ctx.setContextProperty("loadingWinY", y)


def set_window_context(
	engine: QQmlApplicationEngine,
	width: int,
	height: int,
	app: QGuiApplication | None = None,
	**extra: object,
) -> None:
	ctx = engine.rootContext()
	ctx.setContextProperty("initWinWidth", width)
	ctx.setContextProperty("initWinHeight", height)
	ctx.setContextProperty("uiLanguage", TEST_LANGUAGE)
	if app is not None:
		x, y = centered_window_origin(app, width, height)
		ctx.setContextProperty("mainWinX", x)
		ctx.setContextProperty("mainWinY", y)
	for key, value in extra.items():
		ctx.setContextProperty(key, value)


def clear_qml_roots(engine: QQmlApplicationEngine, app: QGuiApplication) -> None:
	for root in list(engine.rootObjects()):
		if hasattr(root, "hide"):
			root.hide()
		if hasattr(root, "close"):
			root.close()
		root.deleteLater()
	app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 200)


def load_qml(
	engine: QQmlApplicationEngine,
	filename: str,
	app: QGuiApplication | None = None,
	*,
	replace: bool = False,
) -> bool:
	if replace and app is not None:
		clear_qml_roots(engine, app)
	engine.load(QUrl.fromLocalFile(str(UI_DIR / filename)))
	loaded = bool(engine.rootObjects())
	if loaded and app is not None:
		sync_window_icons(engine, app)
	return loaded


def close_boot_splash() -> None:
	try:
		import pyi_splash
	except ImportError:
		return
	if pyi_splash.is_alive():
		pyi_splash.close()


def show_loading_screen(
	app: QGuiApplication,
	engine: QQmlApplicationEngine,
) -> bool:
	set_loading_context(engine, app)
	if not load_qml(engine, "loading_screen.qml", app, replace=False):
		return False
	app.processEvents(QEventLoop.ProcessEventsFlag.AllEvents, 100)
	close_boot_splash()
	return True
