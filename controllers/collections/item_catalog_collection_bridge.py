from PySide6.QtCore import QObject, Property, Signal

from config import ITEMS_MAPPING
from core.game_logic.enums import ItemAge, ItemType
from core.game_logic.player.player_equipment_model import ItemModel
from controllers.models.item_model_bridge import ItemModelBridge

TYPE_GRID_ORDER = (
    ItemType.Helmet,
    ItemType.Armour,
    ItemType.Gloves,
    ItemType.Necklace,
    ItemType.Weapon,
    ItemType.Shoes,
    ItemType.Belt,
    ItemType.Ring,
)

AGE_GRID_ORDER = tuple(ItemAge)


def _first_idx_for(age: ItemAge, item_type: ItemType) -> int:
    prefix = f"{age.value}_{item_type.value}_"
    indices: list[int] = []
    for key, entry in ITEMS_MAPPING["items"].items():
        if not key.startswith(prefix):
            continue
        indices.append(int(entry["Idx"]))
    if not indices:
        raise KeyError(f"no item mapping for age={age.value} type={item_type.value}")
    return min(indices)


class ItemCatalogCollectionBridge(QObject):

    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._item_bridges: list[ItemModelBridge] = []
        for age in AGE_GRID_ORDER:
            for item_type in TYPE_GRID_ORDER:
                idx = _first_idx_for(age, item_type)
                item = ItemModel(age, item_type, idx, level=26)
                self._item_bridges.append(ItemModelBridge(item, parent=self))

    @Property("QVariantList", notify=changed)
    def items(self) -> list[ItemModelBridge]:
        return self._item_bridges

    @Property(int, constant=True)
    def itemCount(self) -> int:
        return len(AGE_GRID_ORDER) * len(TYPE_GRID_ORDER)

    @Property(int, constant=True)
    def columnsPerRow(self) -> int:
        return len(TYPE_GRID_ORDER)

    @Property(int, constant=True)
    def rowCount(self) -> int:
        return len(AGE_GRID_ORDER)
