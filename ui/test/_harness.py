from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

TEST_DIR = Path(__file__).resolve().parent
UI_DIR = TEST_DIR.parent
SCRIPTS_ROOT = UI_DIR.parent
UTILS_DIR = UI_DIR / "utils"
DUMP_PATH = SCRIPTS_ROOT / "core_test" / "test_user_dump.txt"
TEST_LANGUAGE = "en"


def bootstrap() -> None:
    for path in (TEST_DIR, UTILS_DIR, SCRIPTS_ROOT):
        text = str(path)
        if text not in sys.path:
            sys.path.insert(0, text)
    os.environ.setdefault("QML_XHR_ALLOW_FILE_READ", "1")
    os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")


def create_app_engine() -> tuple[QGuiApplication, QQmlApplicationEngine]:
    bootstrap()
    from localizer import register_loc_manager
    from ui_settings import register_display_refresh, register_ui_settings
    from number_display_bridge import register_number_display
    from egg_icon_helper import register_egg_icon_helper
    from mount_icon_helper import register_mount_icon_helper
    from pet_icon_helper import register_pet_icon_helper
    from skill_icon_helper import register_skill_icon_helper
    from tech_tree_icon_helper import register_tech_tree_icon_helper

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


def default_window_size(app: QGuiApplication, width_ratio: float = 0.9, height_ratio: float = 0.9) -> tuple[int, int]:
    size = app.primaryScreen().size()
    return int(size.width() * width_ratio), int(size.height() * height_ratio)


def set_window_context(engine: QQmlApplicationEngine, width: int, height: int, **extra: object) -> None:
    ctx = engine.rootContext()
    ctx.setContextProperty("initWinWidth", width)
    ctx.setContextProperty("initWinHeight", height)
    ctx.setContextProperty("uiLanguage", TEST_LANGUAGE)
    for key, value in extra.items():
        ctx.setContextProperty(key, value)


def load_qml(engine: QQmlApplicationEngine, filename: str) -> bool:
    engine.load(QUrl.fromLocalFile(str(TEST_DIR / filename)))
    return bool(engine.rootObjects())


bootstrap()
