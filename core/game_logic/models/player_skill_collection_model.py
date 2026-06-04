from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from ...miraesee_extension import miraesee_extension
from ..enums import Rarity, CombatSkill, AscendableType
from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from .summon_model import SummonModel
from .ascension_model import AscensionModel

if TYPE_CHECKING:
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


class PlayerSkillModel:
	def __init__(
		self,
		type: CombatSkill,
		level: int = 0,
		shard_count: int = 0,
		is_equipped: bool = False,
		equip_slot: int = 0,
	) -> None:
		self.type = type
		self._level = max(0, level)
		self._shard_count = 0 if self.is_maxed() else max(0, shard_count)
		self.is_equipped = is_equipped
		self.equip_slot = equip_slot

	@property
	def level(self) -> int:
		return self._level

	@level.setter
	def level(self, value: int) -> None:
		self._level = max(0, value)
		if self.is_maxed():
			self._shard_count = 0

	@property
	def shard_count(self) -> int:
		return self._shard_count

	@shard_count.setter
	def shard_count(self, value: int) -> None:
		if self.is_maxed():
			self._shard_count = 0
			return
		self._shard_count = max(0, value)

	def is_maxed(self) -> bool:
		return self._level >= MAX_SKILL_LEVEL

	def add_shards(self, amount: int) -> None:
		if amount <= 0 or self.is_maxed():
			if self.is_maxed():
				self._shard_count = 0
			return
		self._shard_count += amount

	def set_shards(self, amount: int) -> None:
		self.shard_count = amount

	def spend_shards(self, amount: int) -> None:
		if amount <= 0:
			return
		self._shard_count = max(0, self._shard_count - amount)
		if self.is_maxed():
			self._shard_count = 0

	def get_passive_stats(self, player_model: PlayerModel):
		raise NotImplementedError("GetPassiveStats requires SharedGameConfig resolution")


class PlayerSkillCollectionModel:
	def __init__(self) -> None:
		self.player_skills: dict[CombatSkill, PlayerSkillModel] = {}
		self.auto_activate_skill_active: bool = False
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Skills)

	# --- Game.Logic.PlayerSkillCollectionModel (stubs) ---

	def ascend(self) -> None:
		raise NotImplementedError

	def are_all_my_skills_maxed(self) -> bool:
		raise NotImplementedError

	def get_empty_slots(self) -> list[int]:
		raise NotImplementedError

	def get_equipped_skills(self) -> list[PlayerSkillModel]:
		raise NotImplementedError

	def get_total_passives(self, player_model: PlayerModel) -> int:
		raise NotImplementedError

	def has_all_skills(self) -> bool:
		raise NotImplementedError

	def try_get_skill_in_slot(self, slot_index: int) -> PlayerSkillModel | None:
		raise NotImplementedError

	@staticmethod
	def max_skill_level() -> int:
		return MAX_SKILL_LEVEL

	def try_get_skill(self, combat_skill: CombatSkill) -> PlayerSkillModel | None:
		return self.player_skills.get(combat_skill)
