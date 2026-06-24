from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_mount_collection_model import PlayerMountCollectionModel
from localizer import ascension_loc_from_level
from mount_model_bridge import MountModelBridge


class MountCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerMountCollectionModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._refresh_bridges()

    def _refresh_bridges(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)
        self._mount_bridges: list[MountModelBridge] = [
            MountModelBridge(mount, parent=self)
            for mount in self._collection.player_mount_models
        ]

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
