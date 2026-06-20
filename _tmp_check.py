import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI_DIR = ROOT / "ui"
sys.path.insert(0, str(UI_DIR))
sys.path.insert(0, str(UI_DIR / "utils"))
sys.path.insert(0, str(ROOT))

os.environ.setdefault("QML_XHR_ALLOW_FILE_READ", "1")
os.environ.setdefault("QT_QUICK_CONTROLS_STYLE", "Fusion")

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl
from localizer import register_loc_manager

app = QGuiApplication(sys.argv)
engine = QQmlApplicationEngine()
engine.warnings.connect(lambda ws: [print(w.toString()) for w in ws])
engine.addImportPath(str(ROOT))
register_loc_manager(engine)

tmp = UI_DIR / "_apptext_test.qml"
tmp.write_text("""\
import QtQuick
import ui 1.0

Window {
    width: 400; height: 200; visible: true
    title: "AppText test"

    Column {
        anchors.centerIn: parent
        spacing: 12

        AppText {
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
            prefix: "Lv. 10"
        }

        AppText {
            pixelSize: 28
            fillColor: "black"
            outlineWeight: 0
            useUiFont: true
            locId: "4980716816252928"
            locTable: "General"
        }
    }

    Component.onCompleted: Theme.language = "ko"
}
""", encoding="utf-8")

engine.load(QUrl.fromLocalFile(str(tmp)))
print("rootObjects:", len(engine.rootObjects()))
if not engine.rootObjects():
    tmp.unlink()
    sys.exit(-1)
sys.exit(app.exec())
