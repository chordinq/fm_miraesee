from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.game_logic.enums import AscensionLevel

if TYPE_CHECKING:
	from core.game_logic.actions.summon.mount_summon_action import SummonedMountsInfo

from controllers.collections.mount_collection_entry_model import MountCollectionEntryModel
from core.game_logic.player.player_mount_collection_model import PlayerMountCollectionModel
from core.game_logic.player.player_model import PlayerModel
from ui.utils.localizer import ascension_loc_from_level
from controllers.models.mount_model_bridge import MountModelBridge
from ui.utils.rarity_counts import count_rarities


class MountCollectionBridge(QObject):

    changed = Signal()
    gridReloaded = Signal()
    entryLayoutChanged = Signal()
    gridWarmupSuppressedChanged = Signal()

    def __init__(
        self,
        collection: PlayerMountCollectionModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._player = player
        self._grid_warmup_suppressed = False
        self._entry_model = MountCollectionEntryModel(self)
        self._mount_bridge_by_guid: dict[str, MountModelBridge] = {}
        self._mount_bridges: list[MountModelBridge] = []
        self._display_mounts: list[MountModelBridge] = []
        self._sync_ascension()
        self._sync_mount_bridges()
        self._sync_entry_model_full()

    @Property(bool, notify=gridWarmupSuppressedChanged)
    def gridWarmupSuppressed(self) -> bool:
        return self._grid_warmup_suppressed

    def set_grid_warmup_suppressed(self, suppressed: bool) -> None:
        if self._grid_warmup_suppressed == suppressed:
            return
        self._grid_warmup_suppressed = suppressed
        self.gridWarmupSuppressedChanged.emit()

    def _discard_bridge(self, bridge: QObject) -> None:
        bridge.setParent(None)
        bridge.deleteLater()

    def _clear_bridge_cache(self) -> None:
        for bridge in self._mount_bridge_by_guid.values():
            self._discard_bridge(bridge)
        self._mount_bridge_by_guid.clear()
        self._mount_bridges = []
        self._display_mounts = []
        self._entry_model.reset_entries([])

    def _sync_ascension(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

    def _mount_sort_key(self, bridge: MountModelBridge) -> tuple:
        try:
            index = self._mount_bridges.index(bridge)
        except ValueError:
            index = 0
        return (not bridge.isEquipped, -bridge.rarity, index)

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

    def _build_sorted_display_entries(self) -> list[MountModelBridge]:
        self._rebuild_mount_display_list()
        return self._display_mounts

    def _sync_entry_model_full(self) -> None:
        entries = self._build_sorted_display_entries()
        self._entry_model.reset_entries(entries)
        self.gridReloaded.emit()
        self.entryLayoutChanged.emit()

    def _find_insert_index(self, bridge: MountModelBridge) -> int:
        sort_key = self._mount_sort_key(bridge)
        for index, entry_bridge in enumerate(self._entry_model.entries()):
            if self._mount_sort_key(entry_bridge) > sort_key:
                return index
        return self._entry_model.rowCount()

    def _reposition_mount_entry(self, mount_guid: str) -> None:
        bridge = self._mount_bridge_by_guid.get(mount_guid)
        if bridge is None:
            return
        old_index = self._entry_model.find_row_by_guid(mount_guid)
        new_index = self._find_insert_index(bridge)
        if old_index < 0:
            self._entry_model.insert_entry(new_index, bridge)
            return
        if new_index == old_index:
            return
        self._entry_model.remove_row(old_index)
        if new_index > old_index:
            new_index -= 1
        self._entry_model.insert_entry(new_index, bridge)

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
        self._sync_entry_model_full()
        self.changed.emit()

    def refresh_stat_texts(self) -> None:
        for bridge in self._mount_bridge_by_guid.values():
            bridge.invalidate_stat_cache()

    @Slot(str)
    def setUiLanguage(self, language: str) -> None:
        self.refresh_localized_texts()

    def refresh_localized_texts(self) -> None:
        for bridge in self._mount_bridge_by_guid.values():
            bridge.refresh_localized()

    def refresh(self, *, resync_existing: bool = False) -> None:
        self._sync_ascension()
        if resync_existing:
            self.refresh_stat_texts()
        self._sync_mount_bridges(resync_existing=resync_existing)
        self._sync_entry_model_full()
        self.changed.emit()

    def patch_after_mount_summon(self, summoned: list[SummonedMountsInfo]) -> None:
        new_bridges: list[MountModelBridge] = []
        for info in summoned:
            mount = info.mount_model
            bridge = self._mount_bridge_by_guid.get(mount.guid)
            if bridge is None:
                bridge = MountModelBridge(mount, self._player, parent=self)
                self._mount_bridge_by_guid[mount.guid] = bridge
                self._mount_bridges.append(bridge)
                new_bridges.append(bridge)
        if not new_bridges:
            return
        self._rarity_counts = count_rarities(
            self._mount_bridges,
            lambda bridge: bridge._rarity,
        )
        for bridge in new_bridges:
            insert_index = self._find_insert_index(bridge)
            self._entry_model.insert_entry(insert_index, bridge)
        self._rebuild_mount_display_list()
        self.entryLayoutChanged.emit()

    def patch_mount_lock(self, mount_guid: str) -> None:
        bridge = self._mount_bridge_by_guid.get(mount_guid)
        if bridge is None:
            return
        bridge.changed.emit()

    def patch_mount_equip_layout(self, *mount_guids: str) -> None:
        affected_guids = [guid for guid in mount_guids if guid]
        for guid in affected_guids:
            bridge = self._mount_bridge_by_guid.get(guid)
            if bridge is not None:
                bridge.changed.emit()
        for guid in affected_guids:
            self._reposition_mount_entry(guid)
        self._rebuild_mount_display_list()
        self.entryLayoutChanged.emit()

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

    @Property(int, notify=entryLayoutChanged)
    def entryCount(self) -> int:
        return self._entry_model.rowCount()

    @Property(QObject, constant=True)
    def entryModel(self) -> MountCollectionEntryModel:
        return self._entry_model

    @Property("QVariantList", notify=changed)
    def rarityCounts(self) -> list[dict[str, int]]:
        return self._rarity_counts
