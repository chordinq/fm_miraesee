from PySide6.QtCore import QObject, QUrl, Slot

from config import SKILLS_MAPPING, SPRITE_SHEETS, SPRITES_DIR
from core.game_logic.enums import AscensionLevel


class SkillIconHelper(QObject):
    @Slot(int, int, int, result="QVariantMap")
    def lookup(self, rarity: int, index: int, ascension_level: int = 0) -> dict:
        if index < 0:
            return {}
        entry = SKILLS_MAPPING.get(f"{rarity}_{index}")
        if entry is None:
            return {}
        try:
            ascension = AscensionLevel(ascension_level)
        except ValueError:
            ascension = AscensionLevel.None_
        sprite_file: str = entry["Sprite"]["File"]
        sheet_key = ascension.name + sprite_file
        sheet = SPRITE_SHEETS[sheet_key]
        sheet_path = SPRITES_DIR / "Skill" / f"{sheet_key}.png"
        return {
            "spriteSheet": QUrl.fromLocalFile(str(sheet_path)).toString(),
            "spriteIndex": int(entry["Sprite"]["Idx"]),
            "sheetCols": int(sheet["cols"]),
            "sheetNativeSize": int(sheet["cols"] * sheet["iconSize"]),
            "rarity": int(entry["Rarity"]),
        }


def register_skill_icon_helper(engine) -> SkillIconHelper:
    instance = SkillIconHelper(parent=engine)
    engine.rootContext().setContextProperty("SkillIconHelper", instance)
    return instance
