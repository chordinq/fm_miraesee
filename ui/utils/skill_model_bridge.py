from PySide6.QtCore import QObject, Property, Signal

from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from core.game_logic.player.player_skill_collection_model import (
    PlayerSkillModel,
    combat_skill_to_skill_id,
)
from localizer import name_loc_from_entry


class SkillModelBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        skill: PlayerSkillModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._skill = skill

        skill_id = combat_skill_to_skill_id(skill.type)
        key = f"{skill_id.rarity.value}_{skill_id.idx}"
        entry = SKILLS_MAPPING[key]

        self._index: int = skill_id.idx
        self._rarity: int = entry["Rarity"]
        self._skill_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)

        next_level_key = str(skill.level + 1)
        if next_level_key in SKILL_UPGRADE_LIBRARY:
            self._max_shard_count: int = SKILL_UPGRADE_LIBRARY[next_level_key]["Shards"]
        else:
            self._max_shard_count = 0

    @Property(int, notify=changed)
    def index(self) -> int:
        return self._index

    @Property(int, notify=changed)
    def rarity(self) -> int:
        return self._rarity

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
