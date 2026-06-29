from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.player.player_pet_collection_model import PlayerEggModel
from ui.utils.localizer import rarity_loc_from_rarity


class EggModelBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        egg: PlayerEggModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._egg = egg
        self._rarity: int = egg.rarity.value
        self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

    @Property(str, notify=changed)
    def rarityLocId(self) -> str:
        return self._rarity_loc_id

    @Property(str, notify=changed)
    def rarityLocTable(self) -> str:
        return self._rarity_loc_table

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._egg.is_equipped

    @Property(int, notify=changed)
    def equipSlot(self) -> int:
        return self._egg.equip_slot

    @Property(str, notify=changed)
    def guid(self) -> str:
        return self._egg.guid

    @Property(str, notify=changed)
    def seedText(self) -> str:
        return f"{self._egg.seed:#018x}"
