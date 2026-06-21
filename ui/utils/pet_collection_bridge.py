from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_pet_collection_model import PlayerPetCollectionModel
from egg_model_bridge import EggModelBridge
from pet_model_bridge import PetModelBridge


class PetCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerPetCollectionModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._refresh_bridges()

    def _refresh_bridges(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._pet_bridges: list[PetModelBridge] = [
            PetModelBridge(pet, ascension_level=ascension_level, parent=self)
            for pet in self._collection.get_pets()
        ]
        self._egg_bridges: list[EggModelBridge] = [
            EggModelBridge(egg, ascension_level=ascension_level, parent=self)
            for egg in self._collection.get_eggs()
        ]

    def refresh(self) -> None:
        self._refresh_bridges()
        self.changed.emit()

    @Property("QVariantList", notify=changed)
    def pets(self) -> list[PetModelBridge]:
        return self._pet_bridges

    @Property("QVariantList", notify=changed)
    def eggs(self) -> list[EggModelBridge]:
        return self._egg_bridges

    @Property(int, notify=changed)
    def petCount(self) -> int:
        return len(self._pet_bridges)

    @Property(int, notify=changed)
    def eggCount(self) -> int:
        return len(self._egg_bridges)

    @Property(int, notify=changed)
    def entryCount(self) -> int:
        return self.petCount + self.eggCount
