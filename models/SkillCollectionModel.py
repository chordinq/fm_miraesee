# models/SkillCollectionModel.py
from configs.enums import Rarity, AscendableType
from models.SkillModel import SkillModel
from models.SummonModel import SummonModel
from models.AscensionModel import AscensionModel

class SkillCollectionModel:
	def __init__(self):
		self.skills = {}
		
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Skills)

	def get_skill(self, rarity: Rarity, idx: int) -> SkillModel:
		temp_skill = SkillModel(rarity, idx)
		skill_enum = temp_skill.combat_skill
		
		if skill_enum not in self.skills:
			self.skills[skill_enum] = temp_skill
			
		return self.skills[skill_enum]

	def add_skill_shards(self, rarity: Rarity, idx: int, amount: int):
		skill = self.get_skill(rarity, idx)
		skill.add_shards(amount)

	def __repr__(self):
		return f"<SkillCollection | Unlocked:{len(self.skills)} | SummonLv:{self.summon_model.level}>"