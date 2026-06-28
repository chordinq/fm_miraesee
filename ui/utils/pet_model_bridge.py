from PySide6.QtCore import QObject, Property, Signal

from config import PETS_MAPPING
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
from core.game_logic.shared_game_config import get_unlocked_pet_slot_count
from localizer import name_loc_from_entry, rarity_loc_from_rarity
from pet_stat_display import build_pet_stat_lines


class PetModelBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        pet: PlayerPetModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._pet = pet
        self._player = player
        self._rebuild()

    def _rebuild(self) -> None:
        pet = self._pet
        player = self._player

        key = f"{pet.pet_id.rarity.value}_{pet.pet_id.id}"
        entry = PETS_MAPPING[key]

        self._guid = pet.guid
        self._index = pet.pet_id.id
        self._rarity = entry["Rarity"]
        self._pet_key = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
        self._stat_lines = build_pet_stat_lines(player, pet)
        self._can_merge = self._compute_can_merge()

    def _compute_can_merge(self) -> bool:
        collection = self._player.player_pet_collection_model
        for pet in collection.pets:
            if pet.guid != self._pet.guid and not pet.is_equipped:
                return True
        for egg in collection.eggs:
            if not egg.is_equipped:
                return True
        return False

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
        return self._pet.level

    @Property(int, notify=changed)
    def equipSlot(self) -> int:
        return self._pet.equip_slot

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._pet.is_equipped

    @Property(bool, notify=changed)
    def canEquip(self) -> bool:
        if self._pet.is_equipped:
            return True
        return get_unlocked_pet_slot_count(self._player) > 0

    @Property(bool, notify=changed)
    def canMerge(self) -> bool:
        return self._can_merge

    @Property(str, notify=changed)
    def petKey(self) -> str:
        return self._pet_key

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
