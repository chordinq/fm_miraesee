from PySide6.QtCore import QObject, Property, Signal

from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from core.game_logic.actions import ActionResult
from core.game_logic.config.shared_game_config import can_be_upgraded, get_unlocked_skill_slot_count
from core.game_logic.enums import Rarity
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import (
	PlayerSkillModel,
	combat_skill_to_skill_id,
)
from core.format.format_skill import (
	format_skill_description,
	format_skill_passive_stat_text,
	get_skill_name,
)
from core.format.localizer import format_bracketed_entity_title
from ui.utils.localizer import desc_loc_from_entry, name_loc_from_entry, rarity_loc_from_rarity


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
		self._title_text = ""
		self._desc_text = ""
		self._passive_stat_text = ""
		self._max_shard_count = self._read_max_shard_count()
		self._rebuild_detail_text()

	def _read_max_shard_count(self) -> int:
		next_level_key = str(self._skill.level + 1)
		if next_level_key in SKILL_UPGRADE_LIBRARY:
			return SKILL_UPGRADE_LIBRARY[next_level_key]["Shards"]
		return 0

	def _rebuild_detail_text(self) -> None:
		self._title_text = format_bracketed_entity_title(
			Rarity(self._rarity),
			get_skill_name(self._skill.type),
		)
		self._desc_text = format_skill_description(self._player, self._skill)
		self._passive_stat_text = format_skill_passive_stat_text(self._player, self._skill)

	def refresh_localized(self) -> None:
		self._rebuild_detail_text()
		self.changed.emit()

	def sync(self) -> None:
		self._rebuild_detail_text()
		self._max_shard_count = self._read_max_shard_count()
		self.changed.emit()

	def refresh(self) -> None:
		self.sync()

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

	@Property(str, notify=changed)
	def titleText(self) -> str:
		return self._title_text

	@Property(str, notify=changed)
	def descText(self) -> str:
		return self._desc_text

	@Property(str, notify=changed)
	def passiveStatText(self) -> str:
		return self._passive_stat_text
