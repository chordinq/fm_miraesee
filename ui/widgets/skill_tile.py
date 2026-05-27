# ui/widgets/skill_tile.py — circular skill icon + level + shard bar
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF, QSize
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.constants.layout import (
    SKILL_CIRCLE_BORDER,
    SKILL_CIRCLE_SIZE,
    SKILL_TILE_H,
    SKILL_TILE_W,
)
from ui.services.collection_entries import CollectionTileData


class _SkillCircle(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(SKILL_CIRCLE_SIZE, SKILL_CIRCLE_SIZE)
        self._fill = "#7a7a72"
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

    def set_content(self, *, fill_color: str, pixmap: QPixmap | None, equipped: bool) -> None:
        self._fill = fill_color
        self._pixmap = pixmap
        self._equipped = equipped
        if equipped:
            self._badge.show()
            self._badge.adjustSize()
            x = (SKILL_CIRCLE_SIZE - self._badge.width()) // 2
            y = (SKILL_CIRCLE_SIZE - self._badge.height()) // 2
            self._badge.move(max(0, x), max(0, y))
            self._badge.raise_()
        else:
            self._badge.hide()
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        inset = SKILL_CIRCLE_BORDER / 2
        rect = QRectF(inset, inset, SKILL_CIRCLE_SIZE - SKILL_CIRCLE_BORDER, SKILL_CIRCLE_SIZE - SKILL_CIRCLE_BORDER)

        path = QPainterPath()
        path.addEllipse(rect)

        # Z-order: circle fill → skill icon → border stroke
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._fill))
        painter.drawPath(path)

        if self._pixmap is not None and not self._pixmap.isNull():
            painter.setClipPath(path)
            pix = self._pixmap
            sw, sh = pix.width(), pix.height()
            scale = max(rect.width() / sw, rect.height() / sh)
            dw = int(sw * scale)
            dh = int(sh * scale)
            x = int(rect.x() + (rect.width() - dw) / 2)
            y = int(rect.y() + (rect.height() - dh) / 2)
            painter.drawPixmap(QRect(x, y, dw, dh), pix)
            painter.setClipping(False)

        painter.setPen(QPen(QColor("#000000"), SKILL_CIRCLE_BORDER))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class SkillCollectionTile(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(SKILL_TILE_W, SKILL_TILE_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._circle = _SkillCircle()
        layout.addWidget(self._circle, 0, Qt.AlignmentFlag.AlignHCenter)

        self._level = QLabel("")
        self._level.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._level.setStyleSheet(
            "color: #ffffff; font-size: 11px; font-weight: bold; background: transparent;"
        )
        layout.addWidget(self._level)

        self._shards = QLabel("")
        self._shards.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._shards.setFixedWidth(SKILL_TILE_W - 8)
        self._shards.setStyleSheet(
            "background-color: #1a1a1a; color: #ffffff; "
            "border: 1px solid #3a3a3a; border-radius: 7px; "
            "padding: 2px 4px; font-size: 9px; font-weight: bold;"
        )
        layout.addWidget(self._shards, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_data(self, data: CollectionTileData) -> None:
        fill = data.frame_color or data.border_color
        self._circle.set_content(fill_color=fill, pixmap=data.pixmap, equipped=data.equipped)
        self._level.setText(data.meta)
        self._shards.setText(data.shard_label or "")

    def sizeHint(self) -> QSize:  # noqa: D102
        return QSize(SKILL_TILE_W, SKILL_TILE_H)
