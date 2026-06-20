import sys
import os
import time
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
UTILS_DIR = CURRENT_DIR / "utils"
PARENT_DIR = CURRENT_DIR.parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))
if str(UTILS_DIR) not in sys.path:
    sys.path.insert(0, str(UTILS_DIR))
if str(PARENT_DIR) not in sys.path:
    sys.path.insert(0, str(PARENT_DIR))

os.environ.setdefault("QML_XHR_ALLOW_FILE_READ", "1")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model
from skill_collection_bridge import SkillCollectionBridge
from localizer import register_loc_manager

TEST_LANGUAGE = "ko"
DUMP_PATH = CURRENT_DIR / "test_dump.txt"


def handle_qml_warnings(warnings):
    for w in warnings:
        print(w.toString())


def main() -> None:
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.warnings.connect(handle_qml_warnings)
    engine.addImportPath(str(PARENT_DIR))
    register_loc_manager(engine)

    screen = app.primaryScreen()
    screen_size = screen.size()
    init_width = int(screen_size.width() * 0.6)
    init_height = int(screen_size.height() * 0.75)

    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    skill_collection_bridge = SkillCollectionBridge(
        player.player_skill_collection_model,
        parent=engine,
    )

    engine.rootContext().setContextProperty("initWinWidth", init_width)
    engine.rootContext().setContextProperty("initWinHeight", init_height)
    engine.rootContext().setContextProperty("uiLanguage", TEST_LANGUAGE)
    engine.rootContext().setContextProperty("testSkillCollection", skill_collection_bridge)

    qml_path = CURRENT_DIR / "test.qml"
    load_start = time.perf_counter()
    engine.load(QUrl.fromLocalFile(str(qml_path)))
    load_ms = (time.perf_counter() - load_start) * 1000
    print(f"QML loaded in {load_ms:.0f}ms ({skill_collection_bridge.skillCount} skills from dump)")

    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
