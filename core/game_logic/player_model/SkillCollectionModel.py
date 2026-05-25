# models/SkillCollectionModel.py
from core.enums import Rarity, AscendableType
from core.game_logic.player_model.SkillModel import SkillModel
from core.game_logic.player_model.SummonModel import SummonModel
from core.game_logic.player_model.AscensionModel import AscensionModel

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