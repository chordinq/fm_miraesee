from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel

if TYPE_CHECKING:
	from core.game_logic.actions.summon.mount_summon_action import SummonedMountsInfo

from core.game_logic.player.player_mount_collection_model import PlayerMountCollectionModel
from core.game_logic.player.player_model import PlayerModel
from ui.utils.localizer import ascension_loc_from_level
from controllers.models.mount_model_bridge import MountModelBridge
from ui.utils.rarity_counts import count_rarities


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
        self._mount_bridge_by_guid: dict[str, MountModelBridge] = {}
        self._mount_bridges: list[MountModelBridge] = []
        self._display_mounts: list[MountModelBridge] = []
        self._sync_ascension()
        self._sync_mount_bridges()

    def _discard_bridge(self, bridge: QObject) -> None:
        bridge.setParent(None)
        bridge.deleteLater()

    def _clear_bridge_cache(self) -> None:
        for bridge in self._mount_bridge_by_guid.values():
            self._discard_bridge(bridge)
        self._mount_bridge_by_guid.clear()
        self._mount_bridges = []
        self._display_mounts = []

    def _sync_ascension(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

    def _rebuild_mount_display_list(self) -> None:
        indexed_mounts = list(enumerate(self._mount_bridges))
        self._display_mounts = [
            bridge
            for _, bridge in sorted(
                indexed_mounts,
                key=lambda item: (
                    not item[1].isEquipped,
                    -item[1].rarity,
                    item[0],
                ),
            )
        ]

    def _sync_mount_bridges(self, *, resync_existing: bool = False) -> None:
        mounts = self._collection.player_mount_models
        active_guids = {mount.guid for mount in mounts}
        for guid in list(self._mount_bridge_by_guid):
            if guid not in active_guids:
                self._discard_bridge(self._mount_bridge_by_guid.pop(guid))

        ordered: list[MountModelBridge] = []
        for mount in mounts:
            bridge = self._mount_bridge_by_guid.get(mount.guid)
            if bridge is None:
                bridge = MountModelBridge(mount, self._player, parent=self)
                self._mount_bridge_by_guid[mount.guid] = bridge
            elif resync_existing:
                bridge.sync()
            ordered.append(bridge)
        self._mount_bridges = ordered
        self._rarity_counts = count_rarities(
            self._mount_bridges,
            lambda bridge: bridge._rarity,
        )
        self._rebuild_mount_display_list()

    def reload(
        self,
        collection: PlayerMountCollectionModel,
        player: PlayerModel,
    ) -> None:
        self._collection = collection
        self._player = player
        self._clear_bridge_cache()
        self._sync_ascension()
        self._sync_mount_bridges()
        self.changed.emit()

    def refresh(self, *, resync_existing: bool = False) -> None:
        self._sync_ascension()
        self._sync_mount_bridges(resync_existing=resync_existing)
        self.changed.emit()

    def patch_after_mount_summon(self, summoned: list[SummonedMountsInfo]) -> None:
        for info in summoned:
            mount = info.mount_model
            bridge = self._mount_bridge_by_guid.get(mount.guid)
            if bridge is None:
                bridge = MountModelBridge(mount, self._player, parent=self)
                self._mount_bridge_by_guid[mount.guid] = bridge
                self._mount_bridges.append(bridge)
        self._rarity_counts = count_rarities(
            self._mount_bridges,
            lambda bridge: bridge._rarity,
        )
        self._rebuild_mount_display_list()
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

    @Property("QVariantList", notify=changed)
    def displayMounts(self) -> list[MountModelBridge]:
        return self._display_mounts

    @Property(int, notify=changed)
    def mountCount(self) -> int:
        return len(self._mount_bridges)

    @Property("QVariantList", notify=changed)
    def rarityCounts(self) -> list[dict[str, int]]:
        return self._rarity_counts
