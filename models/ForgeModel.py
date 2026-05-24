# models/ForgeModel.py
from configs.enums import AscendableType
from models.AscensionModel import AscensionModel

class ForgeModel:
    def __init__(self):
        # C# 원본 PlayerForgeModel 구조 반영 (SummonModel 미사용)
        self.forge_seed = 0
        self.forge_level = 0
        self.forge_count = 0
        
        self.ascension_model = AscensionModel(AscendableType.Forge)
        
        # 시뮬레이터 전용 보너스 확률 (튜토리얼/옵션 설정용)
        self.free_forge_chance = 0.0