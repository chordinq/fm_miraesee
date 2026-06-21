from PySide6.QtCore import QObject, QUrl, Slot

from config import MOUNTS_MAPPING, SPRITE_SHEETS, SPRITES_DIR
from core.game_logic.enums import AscensionLevel


class MountIconHelper(QObject):
    @Slot(int, int, int, result="QVariantMap")
    def lookup(self, rarity: int, index: int, ascension_level: int = 0) -> dict:
        if index < 0:
            return {}
        entry = MOUNTS_MAPPING.get(f"{rarity}_{index}")
        if entry is None:
            return {}
        try:
            ascension = AscensionLevel(ascension_level)
        except ValueError:
            ascension = AscensionLevel.None_
        sprite_file: str = entry["Sprite"]["File"]
        sheet_key = ascension.name + sprite_file
        sheet = SPRITE_SHEETS[sheet_key]
        sheet_path = SPRITES_DIR / "Mount" / f"{sheet_key}.png"
        return {
            "spriteSheet": QUrl.fromLocalFile(str(sheet_path)).toString(),
            "spriteIndex": int(entry["Sprite"]["Idx"]),
            "sheetCols": int(sheet["cols"]),
            "sheetNativeSize": int(sheet["cols"] * sheet["iconSize"]),
            "rarity": int(entry["Rarity"]),
        }


def register_mount_icon_helper(engine) -> MountIconHelper:
    instance = MountIconHelper(parent=engine)
    engine.rootContext().setContextProperty("MountIconHelper", instance)
    return instance
