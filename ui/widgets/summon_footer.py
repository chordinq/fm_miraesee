# ui/widgets/summon_footer.py — bottom summon / history bar
from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QWidget

from ui.constants.layout import FOOTER_HEIGHT, FOOTER_MARGIN_H, FOOTER_MARGIN_V
from ui.constants.styles import muted_button_style, muted_label_style, primary_button_style


class SummonFooter(QWidget):
    """Fixed-height footer: status left, History + Summon right."""

    summon_pressed = Signal()
    history_pressed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("SummonFooter")
        self.setFixedHeight(FOOTER_HEIGHT)

        row = QHBoxLayout(self)
        row.setContentsMargins(FOOTER_MARGIN_H, FOOTER_MARGIN_V, FOOTER_MARGIN_H, FOOTER_MARGIN_V)
        row.setSpacing(8)

        row.addStretch(1)

        hist = QPushButton("History")
        hist.clicked.connect(self.history_pressed.emit)
        hist.setStyleSheet(muted_button_style())
        row.addWidget(hist)

        summon = QPushButton("Summon")
        summon.clicked.connect(self.summon_pressed.emit)
        summon.setStyleSheet(primary_button_style())
        row.addWidget(summon)

    def set_status(self, text: str) -> None:
        """Reserved for future status messages (currently no footer label)."""
        del text
