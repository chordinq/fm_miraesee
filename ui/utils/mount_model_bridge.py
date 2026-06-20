from PySide6.QtCore import QObject, Property, Signal, QUrl

from config import MOUNTS_MAPPING, SPRITE_SHEETS, SPRITES_DIR
from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_mount_collection_model import PlayerMountModel
from localizer import ascension_loc_from_level, name_loc_from_entry


class MountModelBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        mount: PlayerMountModel,
        ascension_level: AscensionLevel = AscensionLevel.None_,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._mount = mount

        key = f"{mount.mount_id.rarity.value}_{mount.mount_id.id}"
        entry = MOUNTS_MAPPING[key]

        self._rarity: int = entry["Rarity"]
        self._sprite_index: int = entry["Sprite"]["Idx"]
        self._mount_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

        sprite_file: str = entry["Sprite"]["File"]
        sheet_key = ascension_level.name + sprite_file
        sheet = SPRITE_SHEETS[sheet_key]

        self._sheet_cols: int = sheet["cols"]
        self._sheet_native_size: int = sheet["cols"] * sheet["iconSize"]

        sheet_path = SPRITES_DIR / "Mount" / f"{sheet_key}.png"
        self._sprite_sheet: str = QUrl.fromLocalFile(str(sheet_path)).toString()

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

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
        return self._mount.level

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._mount.is_equipped

    @Property(str, notify=changed)
    def mountKey(self) -> str:
        return self._mount_key

    @Property(str, notify=changed)
    def nameLocId(self) -> str:
        return self._name_loc_id

    @Property(str, notify=changed)
    def nameLocTable(self) -> str:
        return self._name_loc_table

    @Property(str, notify=changed)
    def ascensionLocId(self) -> str:
        return self._ascension_loc_id

    @Property(str, notify=changed)
    def ascensionLocTable(self) -> str:
        return self._ascension_loc_table
