from PySide6.QtCore import QObject, Property, Signal, QUrl

from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING, SPRITE_SHEETS, SPRITES_DIR
from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_skill_collection_model import (
    PlayerSkillModel,
    combat_skill_to_skill_id,
)
from localizer import ascension_loc_from_level, name_loc_from_entry


class SkillModelBridge(QObject):
    """Read-only QML bridge for PlayerSkillModel."""

    changed = Signal()

    def __init__(
        self,
        skill: PlayerSkillModel,
        ascension_level: AscensionLevel = AscensionLevel.None_,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._skill = skill

        skill_id = combat_skill_to_skill_id(skill.type)
        key = f"{skill_id.rarity.value}_{skill_id.idx}"
        entry = SKILLS_MAPPING[key]

        self._rarity: int = entry["Rarity"]
        self._sprite_index: int = entry["Sprite"]["Idx"]
        self._skill_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

        sprite_file: str = entry["Sprite"]["File"]
        sheet_key = ascension_level.name + sprite_file
        sheet = SPRITE_SHEETS[sheet_key]

        self._sheet_cols: int = sheet["cols"]
        self._sheet_native_size: int = sheet["cols"] * sheet["iconSize"]

        sheet_path = SPRITES_DIR / "Skill" / f"{sheet_key}.png"
        self._sprite_sheet: str = QUrl.fromLocalFile(str(sheet_path)).toString()

        next_level_key = str(skill.level + 1)
        if next_level_key in SKILL_UPGRADE_LIBRARY:
            self._max_shard_count: int = SKILL_UPGRADE_LIBRARY[next_level_key]["Shards"]
        else:
            self._max_shard_count = 0

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

    @Property(int, notify=changed)
    def level(self) -> int:
        return self._skill.level

    @Property(bool, notify=changed)
    def isEquipped(self) -> bool:
        return self._skill.is_equipped

    @Property(int, notify=changed)
    def shardCount(self) -> int:
        return self._skill.shard_count

    @Property(int, notify=changed)
    def maxShardCount(self) -> int:
        return self._max_shard_count

    @Property(str, notify=changed)
    def skillKey(self) -> str:
        return self._skill_key

    @Property(str, notify=changed)
    def nameLocId(self) -> str:
        return self._name_loc_id

    @Property(str, notify=changed)
    def nameLocTable(self) -> str:
        return self._name_loc_table

    @Property(str, notify=changed)
    def ascensionLocId(self) -> str:
        return self._ascension_loc_id

    @Property(str, notify=changed)
    def ascensionLocTable(self) -> str:
        return self._ascension_loc_table
