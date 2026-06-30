from PySide6.QtCore import QObject, Property, Signal

from config import MOUNTS_MAPPING
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_mount_collection_model import PlayerMountModel
from ui.utils.localizer import name_loc_from_entry, rarity_loc_from_rarity
from ui.utils.mount_stat_display import build_mount_stat_lines


class MountModelBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        mount: PlayerMountModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._mount = mount
        self._player = player
        self._rebuild()

    def _rebuild(self) -> None:
        mount = self._mount
        key = f"{mount.mount_id.rarity.value}_{mount.mount_id.id}"
        entry = MOUNTS_MAPPING[key]

        self._guid = mount.guid
        self._index = mount.mount_id.id
        self._rarity = entry["Rarity"]
        self._mount_key = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
        self._stat_lines = build_mount_stat_lines(self._player, mount)
        self._base_stat_lines = [
            line for line in self._stat_lines if not line["secondary"]
        ]
        self._sub_stat_lines = [
            line for line in self._stat_lines if line["secondary"]
        ]

    def refresh(self) -> None:
        self._rebuild()
        self.changed.emit()

    @Property(str, notify=changed)
    def guid(self) -> str:
        return self._guid

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

    @Property(bool, notify=changed)
    def isLocked(self) -> bool:
        return self._mount.is_locked

    @Property(bool, notify=changed)
    def canEquip(self) -> bool:
        return not self._mount.is_equipped

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
    def rarityLocId(self) -> str:
        return self._rarity_loc_id

    @Property(str, notify=changed)
    def rarityLocTable(self) -> str:
        return self._rarity_loc_table

    @Property("QVariantList", notify=changed)
    def statLines(self) -> list[dict[str, object]]:
        return self._stat_lines

    @Property("QVariantList", notify=changed)
    def baseStatLines(self) -> list[dict[str, object]]:
        return self._base_stat_lines

    @Property("QVariantList", notify=changed)
    def subStatLines(self) -> list[dict[str, object]]:
        return self._sub_stat_lines
