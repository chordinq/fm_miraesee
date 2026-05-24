# models/SummonModel.py
class SummonModel:
    def __init__(self, count: int = 0, level: int = 0, seed: int = 0):
        self.count = count
        self.level = level
        self.set_seed(seed)

    def get_seed(self) -> int:
        return self._seed

    def set_seed(self, new_seed: int):
        self._seed = new_seed & 0xFFFFFFFFFFFFFFFF

    def __repr__(self):
        return f"<Summon Lv.{self.level} | Count:{self.count} | Seed:{hex(self._seed)}>"