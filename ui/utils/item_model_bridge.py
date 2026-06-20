from PySide6.QtCore import QObject, Property, Signal, QUrl

from config import ITEMS_MAPPING, SPRITE_SHEETS, SPRITES_DIR
from core.game_logic.player.player_equipment_model import ItemId
from core.game_logic.player.player_equipment_model import ItemModel
from core.game_logic.player.player_item_model import PlayerItemModel
from localizer import name_loc_from_entry


def _item_mapping_key(item_id: ItemId) -> str:
    return f"{item_id.Age.value}_{item_id.Type.value}_{item_id.Idx}"


class ItemModelBridge(QObject):
    """Read-only QML bridge for PlayerItemModel via Items_Mapping."""

    changed = Signal()

    def __init__(
        self,
        item: PlayerItemModel | ItemModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._item = item

        key = _item_mapping_key(item.item_id)
        entry = ITEMS_MAPPING["items"][key]
        sprite = entry["Sprite"]
        sprite_file: str = sprite["File"]
        sheet = SPRITE_SHEETS[sprite_file]

        self._item_age: int = entry["ItemAge"]
        self._item_type: int = entry["ItemType"]
        self._sprite_index: int = sprite["Pos"]
        self._item_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._sheet_cols: int = sheet["cols"]
        self._sheet_native_size: int = sheet["cols"] * sheet["iconSize"]

        sheet_path = SPRITES_DIR / "Equipment" / f"{sprite_file}.png"
        self._sprite_sheet: str = QUrl.fromLocalFile(str(sheet_path)).toString()

    @Property(int, notify=changed)
    def itemAge(self) -> int:
        return self._item_age

    @Property(int, notify=changed)
    def itemType(self) -> int:
        return self._item_type

    @Property(int, notify=changed)
    def spriteIndex(self) -> int:
        return self._sprite_index

    @Property(str, notify=changed)
    def spriteSheet(self) -> str:
        return self._sprite_sheet

    @Property(int, notify=changed)
    def sheetCols(self) -> int:
        return self._sheet_cols

    @Property(int, notify=changed)
    def sheetNativeSize(self) -> int:
        return self._sheet_native_size

    @Property(int, notify=changed)
    def level(self) -> int:
        return self._item.level

    @Property(str, notify=changed)
    def itemKey(self) -> str:
        return self._item_key

    @Property(str, notify=changed)
    def nameLocId(self) -> str:
        return self._name_loc_id

    @Property(str, notify=changed)
    def nameLocTable(self) -> str:
        return self._name_loc_table

    @Property(str, notify=changed)
    def guid(self) -> str:
        return self._item.guid
