from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetCollectionModel
from egg_model_bridge import EggModelBridge
from localizer import ascension_loc_from_level
from pet_model_bridge import PetModelBridge
from rarity_counts import count_rarities


class PetCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerPetCollectionModel,
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

        self._pet_bridges: list[PetModelBridge] = [
            PetModelBridge(pet, self._player, parent=self)
            for pet in self._collection.get_pets()
        ]
        self._egg_bridges: list[EggModelBridge] = [
            EggModelBridge(egg, parent=self)
            for egg in self._collection.get_eggs()
        ]
        self._hatch_slot_count = self._collection.unlocked_hatch_slots_count
        self._hatch_egg_bridges: list[EggModelBridge | None] = [None] * self._hatch_slot_count
        for egg in self._collection.eggs:
            if egg.is_equipped and 0 <= egg.equip_slot < self._hatch_slot_count:
                self._hatch_egg_bridges[egg.equip_slot] = EggModelBridge(egg, parent=self)

        self._pet_rarity_counts = count_rarities(
            self._collection.get_pets(),
            lambda pet: pet.pet_id.rarity.value,
        )
        self._egg_rarity_counts = count_rarities(
            self._collection.get_eggs(),
            lambda egg: egg.rarity.value,
        )

    def reload(
        self,
        collection: PlayerPetCollectionModel,
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
    def pets(self) -> list[PetModelBridge]:
        return self._pet_bridges

    @Property("QVariantList", notify=changed)
    def eggs(self) -> list[EggModelBridge]:
        return self._egg_bridges

    @Property(int, notify=changed)
    def hatchSlotCount(self) -> int:
        return self._hatch_slot_count

    @Property("QVariantList", notify=changed)
    def hatchEggModels(self) -> list[EggModelBridge | None]:
        return self._hatch_egg_bridges

    @Property(int, notify=changed)
    def petCount(self) -> int:
        return len(self._pet_bridges)

    @Property(int, notify=changed)
    def eggCount(self) -> int:
        return len(self._egg_bridges)

    @Property(int, notify=changed)
    def entryCount(self) -> int:
        return self.petCount + self.eggCount

    @Property("QVariantList", notify=changed)
    def petRarityCounts(self) -> list[dict[str, int]]:
        return self._pet_rarity_counts

    @Property("QVariantList", notify=changed)
    def eggRarityCounts(self) -> list[dict[str, int]]:
        return self._egg_rarity_counts
