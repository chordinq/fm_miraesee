from PySide6.QtCore import QObject, Property, Signal

from config import PETS_MAPPING
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
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

        key = f"{pet.pet_id.rarity.value}_{pet.pet_id.id}"
        entry = PETS_MAPPING[key]

        self._index: int = pet.pet_id.id
        self._rarity: int = entry["Rarity"]
        self._pet_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
        self._stat_lines: list[dict[str, object]] = build_pet_stat_lines(player, pet)

    @Property(int, notify=changed)
    def index(self) -> int:
        return self._index

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

    @Property(int, notify=changed)
    def level(self) -> int:
        return self._pet.level

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._pet.is_equipped

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
