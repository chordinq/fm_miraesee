from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from ...miraesee_extension import miraesee_extension
from ..enums import AscendableType, CombatSkill, Rarity
from ..shared_game_config import SharedGameConfig
from ..stats.stat_helper import StatHelper
from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from .ascension_model import AscensionModel
from ..stats.skill_stats import SkillStats
from .summon_model import SummonModel

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig
	from .player_model import PlayerModel

MAX_SKILL_LEVEL = max(int(row["Level"]) for row in SKILL_UPGRADE_LIBRARY.values())


@dataclass(frozen=True)
class SkillId:
	rarity: Rarity
	idx: int

	@miraesee_extension
	def to_combat_skill(self) -> CombatSkill:
		return skill_id_to_combat_skill(self)


@miraesee_extension
def skill_id_to_combat_skill(skill_id: SkillId) -> CombatSkill:
	key = f"{skill_id.rarity.value}_{skill_id.idx}"
	return CombatSkill(SKILLS_MAPPING[key]["Type"])


@miraesee_extension
def combat_skill_to_skill_id(combat_skill: CombatSkill) -> SkillId:
	for key, data in SKILLS_MAPPING.items():
		if data.get("Type") == combat_skill.value:
			rarity_str, idx_str = key.split("_", 1)
			return SkillId(Rarity(int(rarity_str)), int(idx_str))
	raise ValueError(f"No SkillId mapping for {combat_skill!r}")


_EMPTY_EQUIP_SLOT = -1


class PlayerSkillModel:
	type: CombatSkill
	is_equipped: bool
	equip_slot: int
	_shard_count: int
	level: int

	def __init__(self, type: CombatSkill | None = None) -> None:
		if type is None:
			return
		self.type = type
		self.is_equipped = False
		self.equip_slot = _EMPTY_EQUIP_SLOT
		self._shard_count = 0
		self.level = 0

	@property
	def shard_count(self) -> int:
		return self._shard_count

	@shard_count.setter
	def shard_count(self, value: int) -> None:
		self._shard_count = value

	def get_passive_stats(self, player_model: PlayerModel) -> SkillStats:
		from .player_item_stats import get_total_stats

		result = SkillStats()
		game_config = player_model.game_config
		resolved = SharedGameConfig.get_resolved_passive_skill_stats(
			game_config,
			self.type,
			self.level,
			get_total_stats(player_model),
		)
		result.add_to_contributions(resolved)
		return result

	def is_maxed(self, game_config: SharedGameConfig) -> bool:
		if game_config is None:
			raise ValueError("game_config is required")
		library = game_config.skill_upgrade_library
		if not library:
			raise ValueError("skill_upgrade_library is required")
		return len(library) <= self.level

	def add_shards(self, amount: int, client_listener: Any = None) -> None:
		self._shard_count += amount
		if client_listener is None:
			return

	def spend_shards(self, amount: int, client_listener: Any) -> None:
		self._shard_count -= amount
		if client_listener is None:
			raise ValueError("client_listener is required")

	def set_shards(self, amount: int, client_listener: Any) -> None:
		self._shard_count = amount
		if client_listener is None:
			raise ValueError("client_listener is required")

	@miraesee_extension
	def __lt__(self, other: object) -> bool:
		if not isinstance(other, PlayerSkillModel):
			return NotImplemented
		self_id = combat_skill_to_skill_id(self.type)
		other_id = combat_skill_to_skill_id(other.type)
		return (self_id.rarity.value, self.type.value) < (
			other_id.rarity.value,
			other.type.value,
		)

class PlayerSkillCollectionModel:
	def __init__(self) -> None:
		self.player_skills: dict[CombatSkill, PlayerSkillModel] = {}
		self.auto_activate_skill_active: bool = False
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Skills)

	@miraesee_extension
	def get_player_skills(self) -> list[PlayerSkillModel]:
		return sorted(self.player_skills.values())

	def get_equipped_skills(self) -> list[PlayerSkillModel]:
		return sorted(
			(skill for skill in self.player_skills.values() if skill.is_equipped),
			key=lambda skill: skill.equip_slot,
		)

	def try_get_skill_in_slot(self, slot_index: int) -> PlayerSkillModel | None:
		for skill in self.player_skills.values():
			if skill.is_equipped and skill.equip_slot == slot_index:
				return skill
		return None

	def get_total_passives(self, player_model: PlayerModel) -> SkillStats:
		result = SkillStats()
		for skill in self.player_skills.values():
			result.add_to_contributions(skill.get_passive_stats(player_model))
		return result

	def get_empty_slots(self, player: PlayerModel) -> list[int]:
		count = self._get_unlocked_skill_slot_count(player)
		return [
			slot
			for slot in range(count)
			if self.try_get_skill_in_slot(slot) is None
		]

	def ascend(self) -> None:
		self.player_skills.clear()
		self.summon_model.count = 0
		self.ascension_model.ascend()

	def has_all_skills(self, game_config: SharedGameConfig) -> bool:
		return all(
			combat_skill in self.player_skills
			for combat_skill in game_config.skill_library
		)

	def are_all_my_skills_maxed(self, game_config: SharedGameConfig) -> bool:
		return all(
			skill.is_maxed(game_config) for skill in self.player_skills.values()
		)

	@staticmethod
	def max_skill_level() -> int:
		return MAX_SKILL_LEVEL

	def try_get_skill(self, combat_skill: CombatSkill) -> PlayerSkillModel | None:
		return self.player_skills.get(combat_skill)

	@staticmethod
	def _get_unlocked_skill_slot_count(player: Any) -> int:
		return player.game_config.skill_base_config.skill_slots_count
