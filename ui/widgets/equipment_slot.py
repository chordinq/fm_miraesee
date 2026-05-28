# ui/widgets/equipment_slot.py — single forge equipment cell (rounded age frame + icon)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from core.enums import ItemType
from core.game_logic.player_model.ItemModel import ItemModel
from ui.theme.colors import AGE_COLORS, TILE_PLACEHOLDER
from ui.theme.metrics import (
    EQUIP_CAPTION_BOTTOM_INSET,
    EQUIP_ICON_SIZE,
    EQUIP_SLOT_H,
    EQUIP_SLOT_W,

)
from ui.theme.builders import equipment_slot_style
from ui.services.display_level import format_level
from ui.services.localization import item_type_display_name
from ui.services.item_sprites import item_icon_pixmap
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.widgets.icon_frames import EquipmentIconFrame
from ui.widgets.outlined_label import tile_caption_label


class _ForgeIconHost(QWidget):
    """Equipment icon + level caption overlay."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(EQUIP_ICON_SIZE, EQUIP_ICON_SIZE)
        self._frame = EquipmentIconFrame(EQUIP_ICON_SIZE, self)
        self._caption = tile_caption_label(parent=self)
        self._caption.raise_()
        self._place_caption()

    def set_content(
        self,
        *,
        frame_color: str,
        pixmap,
        level_text: str = "",
    ) -> None:
        self._frame.set_content(frame_color=frame_color, pixmap=pixmap)
        self._caption.setText(level_text)
        self._place_caption()

    def _place_caption(self) -> None:
        level_w = self._caption.caption_width()
        level_h = self._caption.caption_height()
        x = (EQUIP_ICON_SIZE - level_w) // 2
        y = EQUIP_ICON_SIZE - EQUIP_CAPTION_BOTTOM_INSET - level_h
        self._caption.setGeometry(x, y, level_w, level_h)
        self._caption.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802
        self._place_caption()
        super().resizeEvent(event)


class EquipmentSlot(QWidget):
    clicked = Signal()

    def __init__(self, slot_type: ItemType, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._slot_type = slot_type
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setObjectName("EquipSlot")
        self.setFixedSize(EQUIP_SLOT_W, EQUIP_SLOT_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(4, 2, 4, 2)
        layout.setSpacing(2)

        self._type_lbl = QLabel(item_type_display_name(slot_type))
        self._type_lbl.setObjectName("EquipSlotType")
        self._type_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._type_lbl)

        self._frame = _ForgeIconHost()
        layout.addWidget(self._frame, 0, Qt.AlignmentFlag.AlignHCenter)

        self._item: ItemModel | None = None
        self.set_item(None)

    def set_item(self, item: ItemModel | None) -> None:
        self._item = item
        self._refresh_labels()

    def refresh_locale(self) -> None:
        self._refresh_labels()

    def _refresh_labels(self) -> None:
        self._type_lbl.setText(item_type_display_name(self._slot_type))
        item = self._item
        if item is None:
            self._frame.set_content(
                frame_color=TILE_PLACEHOLDER,
                pixmap=None,
                level_text="",
            )
            self.setStyleSheet(equipment_slot_style(filled=False))
            return

        age = int(item.age)
        frame_color = AGE_COLORS.get(age, TILE_PLACEHOLDER)
        pix = item_icon_pixmap(
            item,
            EQUIP_ICON_SIZE,
            device_pixel_ratio=default_device_pixel_ratio(),
        )
        self._frame.set_content(
            frame_color=frame_color,
            pixmap=pix,
            level_text=format_level(item.level),
        )
        self.setStyleSheet(equipment_slot_style(filled=True))

    def mousePressEvent(self, event) -> None:  # noqa: N802
        if event.button() == Qt.MouseButton.LeftButton and self._item is not None:
            self.clicked.emit()
        super().mousePressEvent(event)
