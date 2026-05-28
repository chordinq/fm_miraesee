# ui/app.py — application entry
from __future__ import annotations

import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QApplication, QMainWindow

from ui.views.game_root_view import GameRootView
from ui.services.locale import locale_service
from ui.theme.colors import BG
from ui.theme.fonts import apply_app_font, register_app_fonts
from ui.theme.metrics import (
    START_FULLSCREEN,
    WINDOW_DEFAULT_H,
    WINDOW_DEFAULT_W,
    WINDOW_MIN_H,
    WINDOW_MIN_W,
)
from ui.theme.stylesheet import global_stylesheet


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("MIRAESEE")
        self.setMinimumSize(WINDOW_MIN_W, WINDOW_MIN_H)
        self.resize(WINDOW_DEFAULT_W, WINDOW_DEFAULT_H)

        self._root = GameRootView()
        self._root.set_quit_handler(self.close)
        self.setCentralWidget(self._root)


def run() -> None:
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough,
    )
    app = QApplication(sys.argv)
    register_app_fonts()
    _ = locale_service.language
    apply_app_font(app)
    app.setStyle("Fusion")
    app.setStyleSheet(global_stylesheet())
    locale_service.changed.connect(
        lambda: (apply_app_font(app), app.setStyleSheet(global_stylesheet()))
    )

    win = MainWindow()
    win.setStyleSheet(f"QMainWindow {{ background-color: {BG}; }}")
    if START_FULLSCREEN:
        win.showFullScreen()
    else:
        win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
