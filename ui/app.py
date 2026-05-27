# ui/app.py — application entry
from __future__ import annotations

import sys

from PySide6.QtWidgets import QApplication, QMainWindow, QStackedWidget, QVBoxLayout, QWidget

from ui.constants.colors import BG
from ui.constants.layout import (
    START_FULLSCREEN,
    WINDOW_DEFAULT_H,
    WINDOW_DEFAULT_W,
    WINDOW_MIN_H,
    WINDOW_MIN_W,
)
from ui.constants.styles import global_stylesheet
from ui.services.locale import locale_service
from ui.services.session import session_from_dump
from ui.views.dump_view import DumpView
from ui.views.hub_view import HubView


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MIRAESEE")
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.resize(WINDOW_DEFAULT_W, WINDOW_DEFAULT_H)

        root = QWidget()
        root.setObjectName("GameRoot")
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._dump = DumpView()
        self._dump.start_requested.connect(self._on_start)
        self._dump.quit_requested.connect(self.close)
        self._stack.addWidget(self._dump)
        self._stack.setCurrentWidget(self._dump)

    def _on_start(self) -> None:
        self._dump.set_status("Loading dump…")
        QApplication.processEvents()
        try:
            clip = QApplication.clipboard().text()
            if not clip.strip():
                self._dump.set_status("Clipboard is empty — copy the dump first.")
                return
            session = session_from_dump(clip)
            if session is None:
                self._dump.set_status("Failed to parse dump.")
                return
            hub = HubView(session)
            self._stack.addWidget(hub)
            self._stack.setCurrentWidget(hub)
        except Exception as exc:
            self._dump.set_status(f"Error: {exc}")


def run() -> None:
    app = QApplication(sys.argv)
    _ = locale_service.language  # load persisted language before first paint
    app.setStyle("Fusion")
    app.setStyleSheet(global_stylesheet())

    win = MainWindow()
    win.setStyleSheet(f"QMainWindow {{ background-color: {BG}; }}")
    if START_FULLSCREEN:
        win.showFullScreen()
    else:
        win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
