from PySide6.QtCore import QObject, Property, Signal, Slot, QUrl

from config import SPRITES_DIR
from core.game_logic.enums import ItemType
from core.game_logic.player.player_equipment_model import PlayerEquipmentModel
from controllers.models.item_model_bridge import ItemModelBridge, can_bridge_item

SLOT_GRID_ORDER = (
    "helmet",
    "armour",
    "gloves",
    "necklace",
    "weapon",
    "shoes",
    "belt",
    "ring",
)

SLOT_ITEM_TYPES = (
    int(ItemType.Helmet),
    int(ItemType.Armour),
    int(ItemType.Gloves),
    int(ItemType.Necklace),
    int(ItemType.Weapon),
    int(ItemType.Shoes),
    int(ItemType.Belt),
    int(ItemType.Ring),
)

_INVENTORY_TEXTURES_URL = QUrl.fromLocalFile(
    str(SPRITES_DIR / "Equipment" / "InventoryTextures.png")
).toString()


class EquipmentCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        equipment: PlayerEquipmentModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._slot_bridges: list[ItemModelBridge | None] = []
        for slot_name in SLOT_GRID_ORDER:
            item = getattr(equipment, slot_name)
            if item is not None and can_bridge_item(item):
                self._slot_bridges.append(ItemModelBridge(item, parent=self))
            else:
                self._slot_bridges.append(None)

    def reload(self, equipment: PlayerEquipmentModel) -> None:
        self._slot_bridges = []
        for slot_name in SLOT_GRID_ORDER:
            item = getattr(equipment, slot_name)
            if item is not None and can_bridge_item(item):
                self._slot_bridges.append(ItemModelBridge(item, parent=self))
            else:
                self._slot_bridges.append(None)
        self.changed.emit()

    @Property("QVariantList", notify=changed)
    def items(self) -> list[ItemModelBridge | None]:
        return self._slot_bridges

    @Property(int, constant=True)
    def slotCount(self) -> int:
        return len(SLOT_GRID_ORDER)

    @Property("QVariantList", constant=True)
    def slotItemTypes(self) -> list[int]:
        return list(SLOT_ITEM_TYPES)

    @Property(str, constant=True)
    def emptySlotSheetUrl(self) -> str:
        return _INVENTORY_TEXTURES_URL

    @Slot(int, result="QVariant")
    def itemAt(self, index: int):
        if 0 <= index < len(self._slot_bridges):
            return self._slot_bridges[index]
        return None

    @Slot(int, result=int)
    def slotItemType(self, index: int) -> int:
        if 0 <= index < len(SLOT_ITEM_TYPES):
            return SLOT_ITEM_TYPES[index]
        return -1

    @Property(int, constant=True)
    def columnsPerRow(self) -> int:
        return 4

    @Property(int, notify=changed)
    def equippedCount(self) -> int:
        return sum(1 for bridge in self._slot_bridges if bridge is not None)
