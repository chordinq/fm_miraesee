from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

SCRIPTS_ROOT = Path(__file__).resolve().parents[1]
UI_DIR = SCRIPTS_ROOT / "ui"
UI_TEST_DIR = UI_DIR / "test"
DUMP_PATH = SCRIPTS_ROOT / "core_test" / "test_user_dump.txt"
TEST_LANGUAGE = "en"

__all__ = [
    "DUMP_PATH",
    "SCRIPTS_ROOT",
    "UI_DIR",
    "UI_TEST_DIR",
    "TEST_LANGUAGE",
    "bootstrap",
    "create_app_engine",
    "default_window_size",
    "set_window_context",
    "load_qml",
]


def bootstrap() -> None:
    root = str(SCRIPTS_ROOT)
    if root not in sys.path:
        sys.path.insert(0, root)
    os.environ.setdefault("QML_XHR_ALLOW_FILE_READ", "1")
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")


def create_app_engine() -> tuple[QGuiApplication, QQmlApplicationEngine]:
    bootstrap()
    from ui.utils.localizer import register_loc_manager
    from ui.utils.ui_settings import register_ui_settings
    from controllers.common.number_display_bridge import register_number_display
    from ui.utils.egg_icon_helper import register_egg_icon_helper
    from ui.utils.mount_icon_helper import register_mount_icon_helper
    from ui.utils.pet_icon_helper import register_pet_icon_helper
    from ui.utils.skill_icon_helper import register_skill_icon_helper
    from ui.utils.tech_tree_icon_helper import register_tech_tree_icon_helper

    app = QGuiApplication.instance() or QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.addImportPath(str(SCRIPTS_ROOT))
    register_loc_manager(engine)
    register_ui_settings(engine)
    register_number_display(engine)
    register_pet_icon_helper(engine)
    register_egg_icon_helper(engine)
    register_skill_icon_helper(engine)
    register_mount_icon_helper(engine)
    register_tech_tree_icon_helper(engine)
    return app, engine


def default_window_size(
    app: QGuiApplication,
    width_ratio: float = 0.9,
    height_ratio: float = 0.9,
) -> tuple[int, int]:
    size = app.primaryScreen().size()
    return int(size.width() * width_ratio), int(size.height() * height_ratio)


def set_window_context(
    engine: QQmlApplicationEngine,
    width: int,
    height: int,
    **extra: object,
) -> None:
    ctx = engine.rootContext()
    ctx.setContextProperty("initWinWidth", width)
    ctx.setContextProperty("initWinHeight", height)
    ctx.setContextProperty("uiLanguage", TEST_LANGUAGE)
    for key, value in extra.items():
        ctx.setContextProperty(key, value)


def load_qml(engine: QQmlApplicationEngine, filename: str) -> bool:
    engine.load(QUrl.fromLocalFile(str(UI_TEST_DIR / filename)))
    return bool(engine.rootObjects())
