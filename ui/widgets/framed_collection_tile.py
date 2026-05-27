# ui/widgets/framed_collection_tile.py — pet/mount tile with rounded rarity frame + clipped sprite
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.constants.layout import (
    FRAME_BORDER,
    FRAME_RADIUS,
    FRAME_SIZE,
    FRAMED_TILE_H,
    FRAMED_TILE_W,
)
from ui.services.collection_entries import CollectionTileData


class _RarityFrame(QWidget):
    """Rounded rarity-colored plate; sprite is drawn on top and clipped to the plate."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(FRAME_SIZE, FRAME_SIZE)
        self._frame_color = "#4db84a"
        self._pixmap: QPixmap | None = None
        self._equipped = False

        self._badge = QLabel("Equipped", self)
        self._badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._badge.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; "
            "border-radius: 8px; padding: 2px 8px; font-size: 9px; font-weight: bold;"
        )
        self._badge.hide()
        self._badge.adjustSize()

    def set_content(self, *, frame_color: str, pixmap: QPixmap | None, equipped: bool) -> None:
        self._frame_color = frame_color
        self._pixmap = pixmap
        self._equipped = equipped
        if equipped:
            self._badge.show()
            self._badge.adjustSize()
            x = (FRAME_SIZE - self._badge.width()) // 2
            y = (FRAME_SIZE - self._badge.height()) // 2
            self._badge.move(max(0, x), max(0, y))
            self._badge.raise_()
        else:
            self._badge.hide()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        inset = FRAME_BORDER / 2
        plate = QRectF(
            inset,
            inset,
            FRAME_SIZE - FRAME_BORDER,
            FRAME_SIZE - FRAME_BORDER,
        )
        path = QPainterPath()
        path.addRoundedRect(plate, FRAME_RADIUS, FRAME_RADIUS)

        # Z-order: frame fill → pet sprite → border stroke
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._frame_color))
        painter.drawPath(path)

        if self._pixmap is not None and not self._pixmap.isNull():
            painter.setClipPath(path)
            pix = self._pixmap
            sw, sh = pix.width(), pix.height()
            scale = max(FRAME_SIZE / sw, FRAME_SIZE / sh)
            dw = int(sw * scale)
            dh = int(sh * scale)
            x = (FRAME_SIZE - dw) // 2
            y = (FRAME_SIZE - dh) // 2
            painter.drawPixmap(QRect(x, y, dw, dh), pix)
            painter.setClipping(False)

        painter.setPen(QPen(QColor("#000000"), FRAME_BORDER))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class FramedCollectionTile(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(FRAMED_TILE_W, FRAMED_TILE_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._frame = _RarityFrame()
        layout.addWidget(self._frame, 0, Qt.AlignmentFlag.AlignHCenter)

        self._caption = QLabel("")
        self._caption.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._caption.setStyleSheet(
            "color: #ffffff; font-size: 11px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(self._caption)

    def set_data(self, data: CollectionTileData) -> None:
        frame_color = data.frame_color or data.border_color
        self._frame.set_content(
            frame_color=frame_color,
            pixmap=data.pixmap,
            equipped=data.equipped,
        )
        self._caption.setText(data.meta)

    def sizeHint(self) -> QSize:  # noqa: D102
        return QSize(FRAMED_TILE_W, FRAMED_TILE_H)
