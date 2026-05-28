# ui/widgets/slice_button.py — clickable widget with 9-slice Button_0 background
from __future__ import annotations

from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QMouseEvent, QPaintEvent, QPainter
from PySide6.QtWidgets import QSizePolicy, QWidget

from ui.services.button0_texture import BUTTON_0_COLOR, button0_pixmap


class SliceButton(QWidget):
    """Button_0: 4×2 master → fit; pixmap drawn 1:1 (no stretch)."""

    clicked = Signal()

    def __init__(
        self,
        *,
        logical_w: int,
        logical_h: int,
        color_hex: str = BUTTON_0_COLOR,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._logical_w = logical_w
        self._logical_h = logical_h
        self._color_hex = color_hex
        self._bg = None
        self._pressed = False
        self.setFixedSize(logical_w, logical_h)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._rebuild_background()

    def sizeHint(self) -> QSize:  # noqa: N802
        return QSize(self._logical_w, self._logical_h)

    def apply_logical_size(self, logical_w: int, logical_h: int) -> None:
        self._logical_w = logical_w
        self._logical_h = logical_h
        self.setFixedSize(logical_w, logical_h)
        self._rebuild_background()
        self.update()

    def _rebuild_background(self) -> None:
        self._bg = button0_pixmap(self._logical_w, self._logical_h, self._color_hex)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        if self._bg is None or self._bg.isNull():
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        if self._pressed:
            painter.setOpacity(0.88)
        painter.drawPixmap(0, 0, self._bg)
        painter.end()
        super().paintEvent(event)

    def mousePressEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = True
            self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton:
            self._pressed = False
            self.update()
            if self.rect().contains(event.position().toPoint()):
                self.clicked.emit()
        super().mouseReleaseEvent(event)
