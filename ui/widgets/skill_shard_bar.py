# ui/widgets/skill_shard_bar.py — skill shard progress (black track, white fill, text)
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.theme.fonts import TEXT_STYLE_COLLECTION_SMALL, paint_ui_text
from ui.theme.metrics import (
    SKILL_SHARD_BAR_BORDER,
    SKILL_SHARD_BAR_H,
    SKILL_SHARD_BAR_W,
)


class SkillShardBar(QWidget):
    """Capsule: black track, white fill, 2px black border, outlined text on top."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(SKILL_SHARD_BAR_W, SKILL_SHARD_BAR_H)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent, True)
        self._text_style = TEXT_STYLE_COLLECTION_SMALL
        self._current = 0
        self._maximum: int | None = None
        self._label = ""

    def set_progress(self, current: int, maximum: int | None) -> None:
        self._current = max(0, int(current))
        self._maximum = maximum if maximum is None else max(0, int(maximum))
        if self._maximum is None or self._maximum <= 0:
            self._label = f"{self._current}/—"
        else:
            self._label = f"{self._current}/{self._maximum}"
        self.update()

    def _capsule_path(self) -> QPainterPath:
        h = float(self.height())
        path = QPainterPath()
        path.addRoundedRect(QRectF(0, 0, self.width(), h), h / 2, h / 2)
        return path

    def _border_path(self) -> QPainterPath:
        """Capsule inset by half stroke width so 2px border is not clipped at edges."""
        inset = float(SKILL_SHARD_BAR_BORDER) / 2.0
        rect = QRectF(
            inset,
            inset,
            self.width() - 2 * inset,
            self.height() - 2 * inset,
        )
        radius = rect.height() / 2
        path = QPainterPath()
        path.addRoundedRect(rect, radius, radius)
        return path

    def _capsule_rect(self) -> QRectF:
        return QRectF(0, 0, self.width(), self.height())

    def _fill_path(self, capsule: QPainterPath, capsule_rect: QRectF, ratio: float) -> QPainterPath:
        if ratio >= 0.999:
            return capsule
        fill_w = capsule_rect.width() * ratio
        if fill_w <= 0:
            return QPainterPath()
        slice_rect = QPainterPath()
        slice_rect.addRect(QRectF(capsule_rect.left(), capsule_rect.top(), fill_w, capsule_rect.height()))
        return capsule.intersected(slice_rect)

    def _draw_outlined_text(self, painter: QPainter, rect: QRect) -> None:
        metrics = QFontMetrics(self._text_style.font())
        tw = metrics.horizontalAdvance(self._label)
        th = metrics.height()
        x = rect.x() + (rect.width() - tw) / 2.0
        y = rect.y() + (rect.height() - th) / 2.0 + metrics.ascent()
        paint_ui_text(painter, self._label, x, y, self._text_style)

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        capsule = self._capsule_path()
        capsule_rect = self._capsule_rect()

        # 1. Black track (full capsule)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor("#000000"))
        painter.drawPath(capsule)

        # 2. White fill for shard progress
        maximum = self._maximum
        if maximum is not None and maximum > 0:
            ratio = min(1.0, self._current / maximum)
            fill = self._fill_path(capsule, capsule_rect, ratio)
            if not fill.isEmpty():
                painter.setBrush(QColor("#ffffff"))
                painter.drawPath(fill)

        # 3. Black border (no AA — avoids light fringing on gray background)
        border_pen = QPen(QColor("#000000"), float(SKILL_SHARD_BAR_BORDER))
        border_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        border_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        painter.setPen(border_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._border_path())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        # 4. Label on top
        self._draw_outlined_text(painter, self.rect())
