# ui/widgets/equipment_slot.py — single forge equipment cell (rounded age frame + icon)
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.enums import ItemType
from core.game_logic.player_model.ItemModel import ItemModel
from ui.constants.colors import AGE_COLORS, TILE_PLACEHOLDER
from ui.constants.equipment_slots import SLOT_LABELS
from ui.constants.layout import (
    EQUIP_ICON_SIZE,
    EQUIP_SLOT_H,
    EQUIP_SLOT_W,
    FRAME_BORDER,
    FRAME_RADIUS,
)
from ui.constants.styles import equipment_slot_style
from ui.services.display_level import format_level
from ui.services.item_display import age_display_name, item_display_name
from ui.services.item_sprites import item_icon_pixmap


class _AgeIconFrame(QWidget):
    """Rounded square plate tinted by ItemAge; icon clipped inside; border on top."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(EQUIP_ICON_SIZE, EQUIP_ICON_SIZE)
        self._frame_color = TILE_PLACEHOLDER
        self._pixmap: QPixmap | None = None

    def set_content(self, *, frame_color: str, pixmap: QPixmap | None) -> None:
        self._frame_color = frame_color
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        size = EQUIP_ICON_SIZE
        inset = FRAME_BORDER / 2
        plate = QRectF(inset, inset, size - FRAME_BORDER, size - FRAME_BORDER)
        path = QPainterPath()
        path.addRoundedRect(plate, FRAME_RADIUS, FRAME_RADIUS)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(self._frame_color))
        painter.drawPath(path)

        if self._pixmap is not None and not self._pixmap.isNull():
            painter.setClipPath(path)
            pix = self._pixmap
            sw, sh = pix.width(), pix.height()
            scale = max(size / sw, size / sh)
            dw = int(sw * scale)
            dh = int(sh * scale)
            x = (size - dw) // 2
            y = (size - dh) // 2
            painter.drawPixmap(QRect(x, y, dw, dh), pix)
            painter.setClipping(False)

        painter.setPen(QPen(QColor("#000000"), FRAME_BORDER))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)


class EquipmentSlot(QWidget):
    def __init__(self, slot_type: ItemType, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._slot_type = slot_type
        self.setObjectName("EquipSlot")
        self.setFixedSize(EQUIP_SLOT_W, EQUIP_SLOT_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        self._type_lbl = QLabel(SLOT_LABELS.get(slot_type, "?"))
        self._type_lbl.setObjectName("EquipSlotType")
        self._type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._type_lbl)

        self._frame = _AgeIconFrame()
        layout.addWidget(self._frame, 0, Qt.AlignmentFlag.AlignHCenter)

        self._name_lbl = QLabel("—")
        self._name_lbl.setObjectName("EquipSlotName")
        self._name_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name_lbl.setWordWrap(True)
        layout.addWidget(self._name_lbl)

        self._meta_lbl = QLabel("")
        self._meta_lbl.setObjectName("EquipSlotMeta")
        self._meta_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._meta_lbl)

        self.set_item(None)

    def set_item(self, item: ItemModel | None) -> None:
        if item is None:
            self._frame.set_content(frame_color=TILE_PLACEHOLDER, pixmap=None)
            self._name_lbl.setText("—")
            self._meta_lbl.setText("")
            self.setStyleSheet(equipment_slot_style(filled=False))
            return

        age = int(item.age)
        frame_color = AGE_COLORS.get(age, TILE_PLACEHOLDER)
        pix = item_icon_pixmap(item, EQUIP_ICON_SIZE)
        self._frame.set_content(frame_color=frame_color, pixmap=pix)
        self._name_lbl.setText(item_display_name(item))
        self._meta_lbl.setText(f"{format_level(item.level)} · {age_display_name(age)}")
        self.setStyleSheet(equipment_slot_style(filled=True))
