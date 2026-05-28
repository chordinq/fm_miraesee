# ui/views/shell/game_root_div.py — dump | hub stack
from __future__ import annotations

from PySide6.QtWidgets import QApplication, QStackedWidget, QVBoxLayout, QWidget

from ui.services.localization import ui_text
from features.session import session_from_dump
from ui.views.dump_view import DumpView
from ui.views.hub_view import HubView


class GameRootView(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("GameRoot")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._stack = QStackedWidget()
        layout.addWidget(self._stack)

        self._dump = DumpView()
        self._dump.start_requested.connect(self._on_start)
        self._dump.quit_requested.connect(self._on_quit)
        self._stack.addWidget(self._dump)
        self._stack.setCurrentWidget(self._dump)
        self._quit_handler = None

    def set_quit_handler(self, handler) -> None:
        self._quit_handler = handler

    def _on_quit(self) -> None:
        if self._quit_handler is not None:
            self._quit_handler()

    def _on_start(self) -> None:
        self._dump.set_status(ui_text("loading"))
        QApplication.processEvents()
        try:
            clip = QApplication.clipboard().text()
            if not clip.strip():
                self._dump.set_status(ui_text("clipboard_empty"))
                return
            session = session_from_dump(clip)
            if session is None:
                self._dump.set_status(ui_text("parse_failed"))
                return
            hub = HubView(session)
            self._stack.addWidget(hub)
            self._stack.setCurrentWidget(hub)
        except Exception as exc:
            self._dump.set_status(f"Error: {exc}")
