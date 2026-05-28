# ui/widgets/equipped_ribbon.py — vertical "Equipped" ribbon for collection sub-header
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.services.localization import equipped_label
from ui.theme.fonts import TEXT_STYLE_COLLECTION
from ui.theme.metrics import EQUIPPED_BAR_RIBBON_W


class EquippedRibbon(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedWidth(EQUIPPED_BAR_RIBBON_W)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._text = equipped_label()
        self._font = TEXT_STYLE_COLLECTION.font()

    def refresh_locale(self) -> None:
        self._text = equipped_label()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        w, h = self.width(), self.height()
        margin = 6
        ribbon_h = h - margin * 2
        path = QPainterPath()
        path.moveTo(0, margin)
        path.lineTo(w - 14, margin)
        path.lineTo(w, margin + ribbon_h / 2)
        path.lineTo(w - 14, margin + ribbon_h)
        path.lineTo(0, margin + ribbon_h)
        path.closeSubpath()
        painter.setPen(QPen(QColor("#000000"), 2))
        painter.setBrush(QColor("#ffffff"))
        painter.drawPath(path)
        metrics = QFontMetrics(self._font)
        tw = metrics.horizontalAdvance(self._text)
        x = (w - 14 - tw) / 2.0
        y = (h - metrics.height()) / 2.0 + metrics.ascent()
        painter.setPen(QColor("#000000"))
        painter.setFont(self._font)
        painter.drawText(x, y, self._text)
