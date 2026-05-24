# models/SkillCollectionModel.py
from configs.enums import Rarity, AscendableType
from models.SkillModel import SkillModel
from models.SummonModel import SummonModel
from models.AscensionModel import AscensionModel

class SkillCollectionModel:
    def __init__(self):
        self.skills = {} # {CombatSkill Enum : SkillModel}
        
        self.summon_model = SummonModel()
        self.ascension_model = AscensionModel(AscendableType.Skills)

    def get_skill(self, rarity: Rarity, idx: int) -> SkillModel:
        """가챠 결과(Rarity, Idx)를 받아 해당 스킬 모델을 반환하거나 새로 생성합니다."""
        # 1. 임시로 SkillModel을 생성하여 CombatSkill Enum을 알아냄
        temp_skill = SkillModel(rarity, idx)
        skill_enum = temp_skill.combat_skill
        
        if skill_enum not in self.skills:
            self.skills[skill_enum] = temp_skill
            
        return self.skills[skill_enum]

    def add_skill_shards(self, rarity: Rarity, idx: int, amount: int):
        """가챠 시뮬레이터가 이 함수를 호출하여 조각을 추가합니다."""
        skill = self.get_skill(rarity, idx)
        skill.add_shards(amount)

    def __repr__(self):
        return f"<SkillCollection | Unlocked:{len(self.skills)} | SummonLv:{self.summon_model.level}>"