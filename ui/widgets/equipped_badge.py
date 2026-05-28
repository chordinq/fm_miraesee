# ui/widgets/equipped_badge.py — localized "Equipped" overlay (painted capsule)
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.theme.fonts import UI_FONT_SIZE_EQUIPPED_BADGE, paint_ui_text, ui_text_style

_TEXT_STYLE = ui_text_style(UI_FONT_SIZE_EQUIPPED_BADGE, 0)
from ui.theme.metrics import (
    EQUIPPED_BADGE_BG_ALPHA,
    EQUIPPED_BADGE_PAD_X,
    EQUIPPED_BADGE_PAD_Y,
    EquippedBadgePlacement,
    equipped_badge_xy,
)
from ui.services.localization import equipped_label


class EquippedBadge(QWidget):
    """Semi-transparent capsule badge (QPainter — avoids QSS hiding background)."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._text_style = _TEXT_STYLE
        self._text = equipped_label()
        self.hide()
        self._sync_size()

    def _sync_size(self, *, badge_width: int | None = None) -> None:
        metrics = QFontMetrics(self._text_style.font())
        text_h = metrics.ascent() + metrics.descent()
        h = text_h + 2 * EQUIPPED_BADGE_PAD_Y
        if badge_width is not None:
            w = badge_width
        else:
            text_w = metrics.horizontalAdvance(self._text)
            w = text_w + 2 * EQUIPPED_BADGE_PAD_X + 10
        self.setFixedSize(max(w, 1), max(h, 1))

    def refresh_text(self) -> None:
        self._text = equipped_label()
        self._sync_size()
        self.update()

    def place(self, placement: EquippedBadgePlacement) -> None:
        self._sync_size(badge_width=placement.badge_w)
        x, y = equipped_badge_xy(placement, self.width(), self.height())
        self.move(x, y)
        self.raise_()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        if not self._text:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        w, h = self.width(), self.height()
        radius = h / 2.0
        capsule = QPainterPath()
        capsule.addRoundedRect(QRectF(0, 0, w, h), radius, radius)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(26, 26, 26, EQUIPPED_BADGE_BG_ALPHA))
        painter.drawPath(capsule)

        metrics = QFontMetrics(self._text_style.font())
        tw = metrics.horizontalAdvance(self._text)
        text_h = metrics.ascent() + metrics.descent()
        x = (w - tw) / 2.0
        y = (h - text_h) / 2.0 + metrics.ascent()

        paint_ui_text(painter, self._text, x, y, self._text_style)
