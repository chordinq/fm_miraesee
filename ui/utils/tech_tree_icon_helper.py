from PySide6.QtCore import QObject, QUrl, Slot

from config import SPRITE_SHEETS, SPRITES_DIR, TECHTREE_MAPPING


class TechTreeIconHelper(QObject):
    @Slot(int, result="QVariantMap")
    def lookup(self, node_type: int) -> dict:
        if node_type < 0:
            return {}
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type))
        if entry is None:
            return {}
        sprite = entry.get("Sprite")
        if sprite is None:
            return {}
        sprite_file: str = sprite["File"]
        sheet = SPRITE_SHEETS[sprite_file]
        sheet_path = SPRITES_DIR / "TechTree" / f"{sprite_file}.png"
        return {
            "spriteSheet": QUrl.fromLocalFile(str(sheet_path)).toString(),
            "spriteIndex": int(sprite["Idx"]),
            "sheetCols": int(sheet["cols"]),
            "sheetNativeSize": int(sheet["cols"] * sheet["iconSize"]),
        }


def register_tech_tree_icon_helper(engine) -> TechTreeIconHelper:
    instance = TechTreeIconHelper(parent=engine)
    engine.rootContext().setContextProperty("TechTreeIconHelper", instance)
    return instance
