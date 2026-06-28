from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_mount_collection_model import PlayerMountCollectionModel
from core.game_logic.player.player_model import PlayerModel
from localizer import ascension_loc_from_level
from mount_model_bridge import MountModelBridge
from rarity_counts import count_rarities


class MountCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerMountCollectionModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._player = player
        self._refresh_bridges()

    def _refresh_bridges(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)
        self._mount_bridges: list[MountModelBridge] = [
            MountModelBridge(mount, self._player, parent=self)
            for mount in self._collection.player_mount_models
        ]
        self._rarity_counts = count_rarities(
            self._mount_bridges,
            lambda bridge: bridge._rarity,
        )

    def reload(
        self,
        collection: PlayerMountCollectionModel,
        player: PlayerModel,
    ) -> None:
        self._collection = collection
        self._player = player
        self._refresh_bridges()
        self.changed.emit()

    def refresh(self) -> None:
        self._refresh_bridges()
        self.changed.emit()

    @Property(int, notify=changed)
    def ascensionLevel(self) -> int:
        return self._ascension_level

    @Property(str, notify=changed)
    def ascensionLocId(self) -> str:
        return self._ascension_loc_id

    @Property(str, notify=changed)
    def ascensionLocTable(self) -> str:
        return self._ascension_loc_table

    @Property("QVariantList", notify=changed)
    def mounts(self) -> list[MountModelBridge]:
        return self._mount_bridges

    @Property(int, notify=changed)
    def mountCount(self) -> int:
        return len(self._mount_bridges)

    @Property("QVariantList", notify=changed)
    def rarityCounts(self) -> list[dict[str, int]]:
        return self._rarity_counts
