# models/EggModel.py
from configs.enums import Rarity

class EggModel:
    def __init__(self, rarity: Rarity, seed: int):
        self.rarity = rarity
        self.seed = seed
        self.is_equipped = False
        self.equip_slot = 0