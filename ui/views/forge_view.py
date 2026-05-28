# ui/views/forge_view.py — equipped gear (5 + 3 layout) + item detail
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QHBoxLayout, QScrollArea, QVBoxLayout, QWidget

from core.enums import ItemType
from ui.theme.config.equipment_slots import FORGE_EQUIP_BOTTOM, FORGE_EQUIP_TOP
from ui.theme.metrics import EQUIP_GRID_MARGIN, EQUIP_SLOT_GAP
from ui.services.collection_selection import CollectionSelection
from ui.services.detail_content import content_for_selection
from features.session import Session
from ui.widgets.equipment_slot import EquipmentSlot
from ui.widgets.item_detail_panel import ItemDetailPanel


class ForgeView(QWidget):
    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = session
        self._selection: CollectionSelection | None = None

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll_host = QWidget()
        scroll_layout = QVBoxLayout(scroll_host)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

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
            slot.clicked.connect(lambda st=slot_type: self._on_slot_clicked(st))
            grid.addWidget(slot, 0, col)
            self._slots[slot_type] = slot

        for col, slot_type in enumerate(FORGE_EQUIP_BOTTOM):
            slot = EquipmentSlot(slot_type)
            item = equipment.get_equipped_item(slot_type)
            slot.set_item(item)
            slot.clicked.connect(lambda st=slot_type: self._on_slot_clicked(st))
            grid.addWidget(slot, 1, col)
            self._slots[slot_type] = slot

        body_layout.addWidget(grid_host, 0, Qt.AlignmentFlag.AlignHCenter)
        body_layout.addStretch(1)

        scroll.setWidget(body)
        scroll_layout.addWidget(scroll, 1)
        outer.addWidget(scroll_host, 1)

        self._detail = ItemDetailPanel()
        outer.addWidget(self._detail, 0)
        self._detail.show_content(None)

    def _on_slot_clicked(self, slot_type: ItemType) -> None:
        item = self.session.player.equipment.get_equipped_item(slot_type)
        if item is None:
            return
        self._selection = CollectionSelection(
            kind="equipment",
            item=item,
            slot_type=slot_type,
        )
        self._detail.show_content(content_for_selection(self._selection))

    def refresh_locale(self) -> None:
        equipment = self.session.player.equipment
        for slot_type, slot in self._slots.items():
            slot.set_item(equipment.get_equipped_item(slot_type))
            if hasattr(slot, "refresh_locale"):
                slot.refresh_locale()
        if self._selection is not None:
            self._detail.show_content(content_for_selection(self._selection))
