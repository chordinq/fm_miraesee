import os
import sys
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
if str(SCRIPTS_ROOT) not in sys.path:
	sys.path.insert(0, str(SCRIPTS_ROOT))

os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

from ui.TMPText.tmp_text_bridge import TmpTextBridge
from ui.utils.localizer import register_loc_manager

if __name__ == "__main__":
	app = QGuiApplication(sys.argv)
	engine = QQmlApplicationEngine()
	engine.addImportPath(str(SCRIPTS_ROOT))
	engine.addImportPath(str(SCRIPTS_ROOT / "ui"))
	register_loc_manager(engine)
	engine.rootContext().setContextProperty("TmpTextBridge", TmpTextBridge())
	engine.load(QUrl.fromLocalFile(str(Path(__file__).with_name("test_tmptext.qml"))))
	if not engine.rootObjects():
		sys.exit(1)
	sys.exit(app.exec())
