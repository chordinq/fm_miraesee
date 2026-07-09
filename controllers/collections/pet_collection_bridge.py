from PySide6.QtCore import QObject, Property, Signal, Slot

from typing import TYPE_CHECKING

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetCollectionModel

if TYPE_CHECKING:
	from core.game_logic.actions.summon.egg_summon_action import SummonedEggInfo
from controllers.collections.pet_collection_entry_model import PetCollectionEntryModel
from controllers.models.egg_model_bridge import EggModelBridge
from ui.utils.localizer import ascension_loc_from_level
from controllers.models.pet_model_bridge import PetModelBridge
from ui.utils.rarity_counts import count_rarities


class PetCollectionBridge(QObject):

    changed = Signal()
    petsChanged = Signal()
    inventoryEggsChanged = Signal()
    hatchSlotsChanged = Signal()
    gridReloaded = Signal()
    entryLayoutChanged = Signal()
    gridWarmupSuppressedChanged = Signal()

    def __init__(
        self,
        collection: PlayerPetCollectionModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._player = player
        self._ui_language = "en"
        self._grid_warmup_suppressed = False
        self._entry_model = PetCollectionEntryModel(self)
        self._pet_bridge_by_guid: dict[str, PetModelBridge] = {}
        self._egg_bridge_by_guid: dict[str, EggModelBridge] = {}
        self._pet_bridges: list[PetModelBridge] = []
        self._egg_bridges: list[EggModelBridge] = []
        self._display_pets: list[PetModelBridge] = []
        self._display_inventory_eggs: list[EggModelBridge] = []
        self._hatch_egg_bridges: list[EggModelBridge | None] = []
        self._hatch_slot_count = 0
        self._sync_ascension()
        self._sync_pet_bridges()
        self._sync_egg_bridges()
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

    def _clear_bridge_caches(self) -> None:
        for bridge in self._pet_bridge_by_guid.values():
            self._discard_bridge(bridge)
        for bridge in self._egg_bridge_by_guid.values():
            self._discard_bridge(bridge)
        self._pet_bridge_by_guid.clear()
        self._egg_bridge_by_guid.clear()
        self._pet_bridges = []
        self._egg_bridges = []
        self._display_pets = []
        self._display_inventory_eggs = []
        self._hatch_egg_bridges = []
        self._entry_model.reset_entries([])

    def _sync_ascension(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

    def _pet_sort_key(self, bridge: PetModelBridge) -> tuple:
        try:
            index = self._pet_bridges.index(bridge)
        except ValueError:
            index = 0
        return (not bridge.isEquipped, -bridge.rarity, index)

    def _egg_sort_key(self, bridge: EggModelBridge) -> tuple:
        try:
            index = self._egg_bridges.index(bridge)
        except ValueError:
            index = 0
        return (-bridge.rarity, index)

    def _rebuild_inventory_eggs_only(self) -> None:
        indexed_eggs = [
            (index, bridge)
            for index, bridge in enumerate(self._egg_bridges)
            if not bridge.isEquipped
        ]
        self._display_inventory_eggs = [
            bridge
            for _, bridge in sorted(
                indexed_eggs,
                key=lambda item: (
                    -item[1].rarity,
                    item[0],
                ),
            )
        ]

    def _rebuild_display_pets_only(self) -> None:
        indexed_pets = list(enumerate(self._pet_bridges))
        self._display_pets = [
            bridge
            for _, bridge in sorted(
                indexed_pets,
                key=lambda item: (
                    not item[1].isEquipped,
                    -item[1].rarity,
                    item[0],
                ),
            )
        ]

    def _rebuild_pet_display_lists(self) -> None:
        self._rebuild_display_pets_only()
        self._rebuild_inventory_eggs_only()

    def _build_rarity_grouped_entries(self) -> list[tuple[str, QObject]]:
        entries: list[tuple[str, QObject]] = []
        for bridge in self._display_pets:
            if bridge.isEquipped:
                entries.append(("pet", bridge))

        unequipped_by_rarity: dict[int, list[PetModelBridge]] = {}
        for bridge in self._display_pets:
            if bridge.isEquipped:
                continue
            unequipped_by_rarity.setdefault(bridge.rarity, []).append(bridge)

        eggs_by_rarity: dict[int, list[EggModelBridge]] = {}
        for bridge in self._display_inventory_eggs:
            eggs_by_rarity.setdefault(bridge.rarity, []).append(bridge)

        all_rarities = sorted(
            set(unequipped_by_rarity) | set(eggs_by_rarity),
            reverse=True,
        )
        for rarity in all_rarities:
            for bridge in unequipped_by_rarity.get(rarity, []):
                entries.append(("pet", bridge))
            for bridge in eggs_by_rarity.get(rarity, []):
                entries.append(("egg", bridge))
        return entries

    def _first_inventory_egg_in_grid_order(self) -> EggModelBridge | None:
        bridge = self._entry_model.first_egg_bridge()
        if bridge is None:
            return None
        return bridge

    def _sync_entry_model_full(self) -> None:
        self._rebuild_pet_display_lists()
        self._entry_model.reset_entries(self._build_rarity_grouped_entries())
        self.gridReloaded.emit()
        self.entryLayoutChanged.emit()

    def _equipped_pet_entry_count(self) -> int:
        count = 0
        for entry_kind, entry_bridge in self._entry_model.entries():
            if entry_kind == "pet" and entry_bridge.isEquipped:
                count += 1
            else:
                break
        return count

    def _find_equipped_pet_insert_index(self, bridge: PetModelBridge) -> int:
        sort_key = self._pet_sort_key(bridge)
        for index, (entry_kind, entry_bridge) in enumerate(self._entry_model.entries()):
            if entry_kind != "pet" or not entry_bridge.isEquipped:
                return index
            if self._pet_sort_key(entry_bridge) > sort_key:
                return index
        return self._equipped_pet_entry_count()

    def _find_inventory_insert_index(
        self,
        kind: str,
        bridge: PetModelBridge | EggModelBridge,
    ) -> int:
        target_rarity = bridge.rarity
        sort_key = (
            self._pet_sort_key(bridge) if kind == "pet" else self._egg_sort_key(bridge)
        )
        inventory_start = self._equipped_pet_entry_count()
        for index in range(inventory_start, self._entry_model.rowCount()):
            entry_kind, entry_bridge = self._entry_model.entries()[index]
            entry_rarity = entry_bridge.rarity
            if entry_rarity > target_rarity:
                continue
            if entry_rarity < target_rarity:
                return index
            if kind == "pet":
                if entry_kind == "egg":
                    return index
                if self._pet_sort_key(entry_bridge) > sort_key:
                    return index
            elif entry_kind == "egg" and self._egg_sort_key(entry_bridge) > sort_key:
                return index
        return self._entry_model.rowCount()

    def _find_rarity_grouped_insert_index(
        self,
        kind: str,
        bridge: PetModelBridge | EggModelBridge,
    ) -> int:
        if kind == "pet" and bridge.isEquipped:
            return self._find_equipped_pet_insert_index(bridge)
        return self._find_inventory_insert_index(kind, bridge)

    def _insert_display_pet(self, bridge: PetModelBridge) -> None:
        key = self._pet_sort_key(bridge)
        for index, existing in enumerate(self._display_pets):
            if self._pet_sort_key(existing) > key:
                self._display_pets.insert(index, bridge)
                return
        self._display_pets.append(bridge)

    def _insert_display_inventory_egg(self, bridge: EggModelBridge) -> None:
        key = self._egg_sort_key(bridge)
        for index, existing in enumerate(self._display_inventory_eggs):
            if self._egg_sort_key(existing) > key:
                self._display_inventory_eggs.insert(index, bridge)
                return
        self._display_inventory_eggs.append(bridge)

    def _sync_hatch_slots(self) -> None:
        eggs = self._collection.get_eggs()
        slot_count = self._collection.unlocked_hatch_slots_count
        self._hatch_slot_count = slot_count
        hatch: list[EggModelBridge | None] = [None] * slot_count
        for egg in eggs:
            if egg.is_equipped and 0 <= egg.equip_slot < slot_count:
                hatch[egg.equip_slot] = self._egg_bridge_by_guid.get(egg.guid)
        self._hatch_egg_bridges = hatch

    def _sync_pet_bridges(self, *, resync_existing: bool = False) -> None:
        pets = self._collection.get_pets()
        active_guids = {pet.guid for pet in pets}
        for guid in list(self._pet_bridge_by_guid):
            if guid not in active_guids:
                self._discard_bridge(self._pet_bridge_by_guid.pop(guid))

        ordered: list[PetModelBridge] = []
        for pet in pets:
            bridge = self._pet_bridge_by_guid.get(pet.guid)
            if bridge is None:
                bridge = PetModelBridge(pet, self._player, parent=self)
                self._pet_bridge_by_guid[pet.guid] = bridge
            elif resync_existing:
                bridge.sync()
            ordered.append(bridge)
        self._pet_bridges = ordered
        self._pet_rarity_counts = count_rarities(
            pets,
            lambda pet: pet.pet_id.rarity.value,
        )

    def _sync_egg_bridges(self, *, resync_existing: bool = False) -> None:
        eggs = self._collection.get_eggs()
        active_guids = {egg.guid for egg in eggs}
        for guid in list(self._egg_bridge_by_guid):
            if guid not in active_guids:
                self._discard_bridge(self._egg_bridge_by_guid.pop(guid))

        ordered: list[EggModelBridge] = []
        for egg in eggs:
            bridge = self._egg_bridge_by_guid.get(egg.guid)
            if bridge is None:
                bridge = EggModelBridge(
                    egg,
                    self._player,
                    parent=self,
                    language=self._ui_language,
                )
                self._egg_bridge_by_guid[egg.guid] = bridge
            elif resync_existing or egg.is_equipped:
                bridge.sync()
            ordered.append(bridge)
        self._egg_bridges = ordered

        self._sync_hatch_slots()
        self._egg_rarity_counts = count_rarities(
            eggs,
            lambda egg: egg.rarity.value,
        )

    def patch_pet_lock(self, pet_guid: str) -> None:
        bridge = self._pet_bridge_by_guid.get(pet_guid)
        if bridge is None:
            return
        bridge.changed.emit()

    def patch_pet_equip_layout(self, pet_guid: str, displaced_guid: str | None = None) -> None:
        affected_guids = [
            guid
            for guid in (pet_guid, displaced_guid)
            if guid
        ]
        for guid in affected_guids:
            bridge = self._pet_bridge_by_guid.get(guid)
            if bridge is not None:
                bridge.changed.emit()
        self._rebuild_pet_display_lists()
        for guid in affected_guids:
            self._reposition_pet_entry(guid)
        self.entryLayoutChanged.emit()

    def _reposition_pet_entry(self, pet_guid: str) -> None:
        bridge = self._pet_bridge_by_guid.get(pet_guid)
        if bridge is None:
            return
        old_index = self._entry_model.find_row_by_guid(pet_guid)
        new_index = self._find_rarity_grouped_insert_index("pet", bridge)
        if old_index < 0:
            self._entry_model.insert_entry(new_index, "pet", bridge)
            return
        if new_index == old_index:
            return
        self._entry_model.remove_row(old_index)
        if new_index > old_index:
            new_index -= 1
        self._entry_model.insert_entry(new_index, "pet", bridge)

    def reload(
        self,
        collection: PlayerPetCollectionModel,
        player: PlayerModel,
    ) -> None:
        self._collection = collection
        self._player = player
        self._clear_bridge_caches()
        self._sync_ascension()
        self._sync_pet_bridges()
        self._sync_egg_bridges()
        self._sync_entry_model_full()
        self.hatchSlotsChanged.emit()
        self.changed.emit()

    def refresh(self, *, resync_existing: bool = False) -> None:
        self._sync_ascension()
        self._sync_pet_bridges(resync_existing=resync_existing)
        self._sync_egg_bridges(resync_existing=resync_existing)
        self._sync_entry_model_full()
        self.hatchSlotsChanged.emit()
        self.changed.emit()

    def refresh_stat_texts(self) -> None:
        for bridge in self._pet_bridge_by_guid.values():
            bridge.invalidate_stat_cache()

    def refresh_localized_texts(self) -> None:
        for bridge in self._pet_bridge_by_guid.values():
            bridge.refresh_localized()

    def refresh_eggs(self, *, resync_existing: bool = False) -> None:
        self._sync_egg_bridges(resync_existing=resync_existing)
        self._sync_entry_model_full()
        self.hatchSlotsChanged.emit()
        self.changed.emit()

    def refresh_after_hatch(self) -> None:
        self._sync_pet_bridges(resync_existing=False)
        self._sync_egg_bridges(resync_existing=False)
        self._sync_entry_model_full()
        self.hatchSlotsChanged.emit()
        self.changed.emit()

    def _remove_inventory_egg_display(self, egg_guid: str) -> None:
        for index, bridge in enumerate(self._display_inventory_eggs):
            if bridge.guid == egg_guid:
                self._display_inventory_eggs.pop(index)
                return

    def patch_egg_moved_to_hatch(self, egg_guid: str) -> None:
        bridge = self._egg_bridge_by_guid.get(egg_guid)
        if bridge is not None:
            bridge.sync_quiet()
        self._sync_hatch_slots()
        removed = self._entry_model.remove_egg_by_guid(egg_guid)
        if removed:
            self._remove_inventory_egg_display(egg_guid)
        self.hatchSlotsChanged.emit()
        if removed:
            self.inventoryEggsChanged.emit()
            self.entryLayoutChanged.emit()

    def patch_egg_timer(self, egg_guid: str) -> None:
        bridge = self._egg_bridge_by_guid.get(egg_guid)
        if bridge is not None:
            bridge.sync_quiet()
        self.hatchSlotsChanged.emit()

    def patch_after_egg_summon(self, summoned: list[SummonedEggInfo]) -> None:
        new_bridges: list[EggModelBridge] = []
        for info in summoned:
            egg = info.egg_model
            if egg.guid in self._egg_bridge_by_guid:
                continue
            bridge = EggModelBridge(
                egg,
                self._player,
                parent=self,
                language=self._ui_language,
            )
            self._egg_bridge_by_guid[egg.guid] = bridge
            self._egg_bridges.append(bridge)
            self._insert_display_inventory_egg(bridge)
            new_bridges.append(bridge)
        if not new_bridges:
            return
        self._egg_rarity_counts = count_rarities(
            self._collection.get_eggs(),
            lambda egg: egg.rarity.value,
        )
        for bridge in new_bridges:
            insert_index = self._find_rarity_grouped_insert_index("egg", bridge)
            self._entry_model.insert_entry(insert_index, "egg", bridge)
        self.inventoryEggsChanged.emit()
        self.entryLayoutChanged.emit()

    def patch_after_hatch(self, egg_guid: str) -> None:
        egg_bridge = self._egg_bridge_by_guid.pop(egg_guid, None)
        if egg_bridge is not None:
            self._discard_bridge(egg_bridge)
        self._egg_bridges = [
            bridge for bridge in self._egg_bridges if bridge.guid != egg_guid
        ]

        new_pets: list[PetModelBridge] = []
        known_pet_guids = set(self._pet_bridge_by_guid)
        for pet in self._collection.get_pets():
            if pet.guid in known_pet_guids:
                continue
            bridge = PetModelBridge(pet, self._player, parent=self)
            self._pet_bridge_by_guid[pet.guid] = bridge
            self._pet_bridges.append(bridge)
            new_pets.append(bridge)

        self._pet_rarity_counts = count_rarities(
            self._collection.get_pets(),
            lambda pet: pet.pet_id.rarity.value,
        )
        self._egg_rarity_counts = count_rarities(
            self._collection.get_eggs(),
            lambda egg: egg.rarity.value,
        )
        if self._entry_model.remove_egg_by_guid(egg_guid):
            self._remove_inventory_egg_display(egg_guid)
            self.inventoryEggsChanged.emit()
        for bridge in new_pets:
            self._insert_display_pet(bridge)
            insert_index = self._find_rarity_grouped_insert_index("pet", bridge)
            self._entry_model.insert_entry(insert_index, "pet", bridge)
        self._sync_hatch_slots()
        self.petsChanged.emit()
        self.hatchSlotsChanged.emit()
        if new_pets:
            self.entryLayoutChanged.emit()
        self.changed.emit()

    @Slot(str)
    def setUiLanguage(self, language: str) -> None:
        self.set_ui_language(language)

    def set_ui_language(self, language: str) -> None:
        if language == self._ui_language:
            return
        self._ui_language = language
        self.refresh_localized_texts()
        for bridge in self._egg_bridge_by_guid.values():
            bridge.set_ui_language(language)
        self.changed.emit()

    @Property(QObject, constant=True)
    def entryModel(self) -> PetCollectionEntryModel:
        return self._entry_model

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
    def pets(self) -> list[PetModelBridge]:
        return self._pet_bridges

    @Property("QVariantList", notify=petsChanged)
    def displayPets(self) -> list[PetModelBridge]:
        return self._display_pets

    @Property("QVariantList", notify=changed)
    def eggs(self) -> list[EggModelBridge]:
        return self._egg_bridges

    @Property("QVariantList", notify=inventoryEggsChanged)
    def displayInventoryEggs(self) -> list[EggModelBridge]:
        return self._display_inventory_eggs

    @Property(int, notify=hatchSlotsChanged)
    def hatchSlotCount(self) -> int:
        return self._hatch_slot_count

    @Property("QVariantList", notify=hatchSlotsChanged)
    def hatchEggModels(self) -> list[EggModelBridge | None]:
        return self._hatch_egg_bridges

    @Property(int, notify=changed)
    def petCount(self) -> int:
        return len(self._pet_bridges)

    @Property(int, notify=changed)
    def eggCount(self) -> int:
        return len(self._egg_bridges)

    @Property(int, notify=entryLayoutChanged)
    def entryCount(self) -> int:
        return self._entry_model.rowCount()

    @Property(QObject, notify=inventoryEggsChanged)
    def firstInventoryEgg(self) -> EggModelBridge | None:
        return self._first_inventory_egg_in_grid_order()

    @Property("QVariantList", notify=changed)
    def petRarityCounts(self) -> list[dict[str, int]]:
        return self._pet_rarity_counts

    @Property("QVariantList", notify=changed)
    def eggRarityCounts(self) -> list[dict[str, int]]:
        return self._egg_rarity_counts
