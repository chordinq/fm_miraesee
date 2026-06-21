from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.player.player_pet_collection_model import PlayerEggModel


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

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._egg.is_equipped

    @Property(int, notify=changed)
    def equipSlot(self) -> int:
        return self._egg.equip_slot

    @Property(str, notify=changed)
    def guid(self) -> str:
        return self._egg.guid
