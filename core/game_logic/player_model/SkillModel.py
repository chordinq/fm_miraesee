# core/game_logic/player_model/SkillModel.py
from core.enums import CombatSkill, Rarity
from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING

class SkillModel:
	def __init__(self, rarity: Rarity, idx: int):
		self.rarity = rarity
		self.idx = idx
		self.level = 0
		self.shard_count = 0
		self.is_equipped = False
		self.equip_slot = 0

	def _mapping_entry(self) -> dict:
		key = f"{self.rarity.value}_{self.idx}"
		entry = SKILLS_MAPPING.get(key)
		if not entry:
			raise ValueError(f"Unknown Skill. (Rarity: {self.rarity.name}, Idx: {self.idx})")
		return entry

	@property
	def combat_skill(self) -> CombatSkill:
		return CombatSkill(self._mapping_entry()["Enum"])

	@property
	def name(self) -> str:
		entry = self._mapping_entry()
		return entry.get("Key", "Unknown")

	def add_shards(self, amount: int) -> None:
		self.shard_count += amount
		self._apply_level_ups()

	def _apply_level_ups(self) -> None:
		while True:
			nxt = self.level + 1
			entry = SKILL_UPGRADE_LIBRARY.get(str(nxt))
			if not entry:
				return
			cost = int(entry["Shards"])
			if self.shard_count < cost:
				return
			self.shard_count -= cost
			self.level += 1

	def __repr__(self) -> str:
		return (
			f"<Skill {self.name}({self.combat_skill.name}) | "
			f"Lv.{self.level} | Shards:{self.shard_count}>"
		)
