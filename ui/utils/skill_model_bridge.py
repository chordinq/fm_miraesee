from PySide6.QtCore import QObject, Property, Signal

from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from core.game_logic.actions import ActionResult
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.shared_game_config import can_be_upgraded, get_unlocked_skill_slot_count
from core.game_logic.player.player_skill_collection_model import (
    PlayerSkillModel,
    combat_skill_to_skill_id,
)
from localizer import desc_loc_from_entry, name_loc_from_entry, rarity_loc_from_rarity
from skill_stat_display import format_skill_description_args


class SkillModelBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        skill: PlayerSkillModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._skill = skill
        self._player = player

        skill_id = combat_skill_to_skill_id(skill.type)
        key = f"{skill_id.rarity.value}_{skill_id.idx}"
        entry = SKILLS_MAPPING[key]

        self._index: int = skill_id.idx
        self._rarity: int = entry["Rarity"]
        self._skill_key: str = entry["Key"]
        self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
        self._desc_loc_id, self._desc_loc_table = desc_loc_from_entry(entry)
        self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
        self._desc_format_args: list[str] = format_skill_description_args(player, skill)

        next_level_key = str(skill.level + 1)
        if next_level_key in SKILL_UPGRADE_LIBRARY:
            self._max_shard_count: int = SKILL_UPGRADE_LIBRARY[next_level_key]["Shards"]
        else:
            self._max_shard_count = 0

    def refresh(self) -> None:
        self._desc_format_args = format_skill_description_args(self._player, self._skill)
        self.changed.emit()

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
    def combatSkillType(self) -> int:
        return int(self._skill.type.value)

    @Property(int, notify=changed)
    def equipSlot(self) -> int:
        return self._skill.equip_slot

    @Property(bool, notify=changed)
    def canUpgrade(self) -> bool:
        result, _ = can_be_upgraded(self._skill, self._player)
        return result == ActionResult.Success

    @Property(bool, notify=changed)
    def canEquip(self) -> bool:
        if self._skill.is_equipped:
            return True
        return get_unlocked_skill_slot_count(self._player) > 0

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
    def descLocId(self) -> str:
        return self._desc_loc_id

    @Property(str, notify=changed)
    def descLocTable(self) -> str:
        return self._desc_loc_table

    @Property(str, notify=changed)
    def rarityLocId(self) -> str:
        return self._rarity_loc_id

    @Property(str, notify=changed)
    def rarityLocTable(self) -> str:
        return self._rarity_loc_table

    @Property("QVariantList", notify=changed)
    def descFormatArgs(self) -> list[str]:
        return self._desc_format_args
