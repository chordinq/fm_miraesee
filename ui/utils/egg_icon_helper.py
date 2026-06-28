from PySide6.QtCore import QObject, QUrl, Slot

from config import SPRITES_DIR
from core.game_logic.enums import AscensionLevel


def _egg_sheet_filename(ascension_level: AscensionLevel) -> str:
    if ascension_level == AscensionLevel.None_:
        return "Eggs.png"
    return f"{ascension_level.name}Eggs.png"


class EggIconHelper(QObject):
    @Slot(int, int, result="QVariantMap")
    def lookup(self, rarity: int, ascension_level: int = 0) -> dict:
        if rarity < 0:
            return {}
        try:
            ascension = AscensionLevel(ascension_level)
        except ValueError:
            ascension = AscensionLevel.None_
        sheet_path = SPRITES_DIR / "Egg" / _egg_sheet_filename(ascension)
        return {
            "spriteSheet": QUrl.fromLocalFile(str(sheet_path)).toString(),
            "spriteIndex": rarity,
            "sheetCols": 4,
            "sheetNativeSize": 1024,
        }


def register_egg_icon_helper(engine) -> EggIconHelper:
    instance = EggIconHelper(parent=engine)
    engine.rootContext().setContextProperty("EggIconHelper", instance)
    return instance
