from PySide6.QtCore import QObject, Property, Signal

from config import MOUNTS_MAPPING
from core.game_logic.player.player_mount_collection_model import PlayerMountModel
from localizer import name_loc_from_entry


class MountModelBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        mount: PlayerMountModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._mount = mount

        key = f"{mount.mount_id.rarity.value}_{mount.mount_id.id}"
        entry = MOUNTS_MAPPING[key]

        self._index: int = mount.mount_id.id
        self._rarity: int = entry["Rarity"]
        self._mount_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)

    @Property(int, notify=changed)
    def index(self) -> int:
        return self._index

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

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
