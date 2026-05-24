# models/SkillModel.py
from configs.enums import Rarity, CombatSkill
from configs import SKILL_MAPPING

class SkillModel:
	def __init__(self, rarity: Rarity, idx: int):
		self.rarity = rarity
		self.idx = idx
		
		self.level = 0
		self.shard_count = 0
		self.is_equipped = False
		self.equip_slot = 0

	@property
	def combat_skill(self) -> CombatSkill:
		mapping_key = f"{self.rarity.value}_{self.idx}"
		mapping_data = SKILL_MAPPING.get(mapping_key)
		if mapping_data:
			return CombatSkill(mapping_data["Enum"])
		raise ValueError(f"Unknown Skill. (Rarity: {self.rarity.name}, Idx: {self.idx})")

	@property
	def name(self) -> str:
		mapping_key = f"{self.rarity.value}_{self.idx}"
		mapping_data = SKILL_MAPPING.get(mapping_key)
		return mapping_data["Kor"] if mapping_data else "Unknown"

	def add_shards(self, amount: int):
		self.shard_count += amount

	def __repr__(self):
		return f"<Skill {self.name}({self.combat_skill.name}) | Lv.{self.level} | Shards:{self.shard_count}>"