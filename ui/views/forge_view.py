# ui/views/forge_view.py — equipped gear (5 + 3 layout)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QScrollArea, QVBoxLayout, QWidget

from core.enums import ItemType
from ui.constants.equipment_slots import FORGE_EQUIP_BOTTOM, FORGE_EQUIP_TOP
from ui.constants.layout import EQUIP_GRID_MARGIN, EQUIP_SLOT_GAP
from ui.services.session import Session
from ui.widgets.equipment_slot import EquipmentSlot


class ForgeView(QWidget):
    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = session

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.addStretch(1)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(EQUIP_GRID_MARGIN, EQUIP_GRID_MARGIN, EQUIP_GRID_MARGIN, EQUIP_GRID_MARGIN)
        grid.setSpacing(EQUIP_SLOT_GAP)

        equipment = session.player.equipment
        self._slots: dict[ItemType, EquipmentSlot] = {}

        for col, slot_type in enumerate(FORGE_EQUIP_TOP):
            slot = EquipmentSlot(slot_type)
            item = equipment.get_equipped_item(slot_type)
            slot.set_item(item)
            grid.addWidget(slot, 0, col)
            self._slots[slot_type] = slot

        for col, slot_type in enumerate(FORGE_EQUIP_BOTTOM):
            slot = EquipmentSlot(slot_type)
            item = equipment.get_equipped_item(slot_type)
            slot.set_item(item)
            grid.addWidget(slot, 1, col)
            self._slots[slot_type] = slot

        body_layout.addWidget(grid_host, 0, Qt.AlignmentFlag.AlignHCenter)
        body_layout.addStretch(1)

        scroll.setWidget(body)
        outer.addWidget(scroll, 1)

    def refresh_locale(self) -> None:
        equipment = self.session.player.equipment
        for slot_type, slot in self._slots.items():
            slot.set_item(equipment.get_equipped_item(slot_type))
