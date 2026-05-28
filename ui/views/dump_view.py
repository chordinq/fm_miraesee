# ui/views/dump_view.py — paste dump, then Start (layout + click wiring in one place)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget

from ui.theme.metrics import DUMP_BTN_SPACING, DUMP_BTN_WIDTH, DUMP_CENTER_SPACING
from ui.theme.builders import (
    dump_quit_button_style,
    dump_start_button_style,
    muted_label_style,
    title_label_style,
)


class DumpView(QWidget):
    start_requested = Signal()
    quit_requested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addStretch(1)

        center = QWidget()
        col = QVBoxLayout(center)
        col.setSpacing(DUMP_CENTER_SPACING)
        col.setAlignment(Qt.AlignmentFlag.AlignCenter)

        title = QLabel("MIRAESEE")
        title.setStyleSheet(title_label_style())
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(title)

        sub = QLabel("v1.0.0 · by chordinq")
        sub.setStyleSheet(muted_label_style())
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(sub)

        self._status = QLabel("Ready. Copy dump, then press Start.")
        self._status.setStyleSheet(muted_label_style())
        self._status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(self._status)

        hint = QLabel(
            "1. Copy your game dump in-game (Ctrl+C)\n"
            "2. Click Start — clipboard is read automatically"
        )
        hint.setStyleSheet(muted_label_style())
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        col.addWidget(hint)

        row = QWidget()
        brow = QVBoxLayout(row)
        brow.setSpacing(DUMP_BTN_SPACING)
        brow.setAlignment(Qt.AlignmentFlag.AlignCenter)

        start = QPushButton("Start")
        start.setFixedWidth(DUMP_BTN_WIDTH)
        start.clicked.connect(self._on_start_clicked)
        start.setStyleSheet(dump_start_button_style())
        brow.addWidget(start, alignment=Qt.AlignmentFlag.AlignCenter)

        quit_btn = QPushButton("Quit")
        quit_btn.setFixedWidth(DUMP_BTN_WIDTH)
        quit_btn.clicked.connect(self.quit_requested.emit)
        quit_btn.setStyleSheet(dump_quit_button_style())
        brow.addWidget(quit_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        col.addWidget(row)

        layout.addWidget(center, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addStretch(1)

    def _on_start_clicked(self) -> None:
        self._status.setText("Loading…")
        self.start_requested.emit()

    def set_status(self, msg: str) -> None:
        self._status.setText(msg)
