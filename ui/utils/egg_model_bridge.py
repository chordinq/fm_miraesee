from PySide6.QtCore import QObject, Property, Signal, QUrl

from config import SPRITES_DIR
from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_pet_collection_model import PlayerEggModel


def _egg_sheet_filename(ascension_level: AscensionLevel) -> str:
    if ascension_level == AscensionLevel.None_:
        return "Eggs.png"
    return f"{ascension_level.name}Eggs.png"


class EggModelBridge(QObject):
    """Read-only QML bridge for PlayerEggModel."""

    changed = Signal()

    def __init__(
        self,
        egg: PlayerEggModel,
        ascension_level: AscensionLevel = AscensionLevel.None_,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._egg = egg

        self._rarity: int = egg.rarity.value
        self._sprite_index: int = egg.rarity.value
        self._sheet_cols: int = 8
        self._sheet_native_size: int = 2048

        sheet_path = SPRITES_DIR / "Egg" / _egg_sheet_filename(ascension_level)
        self._sprite_sheet: str = QUrl.fromLocalFile(str(sheet_path)).toString()

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

    @Property(int, notify=changed)
    def spriteIndex(self) -> int:
        return self._sprite_index

    @Property(str, notify=changed)
    def spriteSheet(self) -> str:
        return self._sprite_sheet

    @Property(int, notify=changed)
    def sheetCols(self) -> int:
        return self._sheet_cols

    @Property(int, notify=changed)
    def sheetNativeSize(self) -> int:
        return self._sheet_native_size

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._egg.is_equipped

    @Property(str, notify=changed)
    def guid(self) -> str:
        return self._egg.guid
