# models/SecondaryStatsModel.py
from core.game_logic.player_model.StatModel import StatModel

class SecondaryStatsModel:
	def __init__(self):
		self.stats = []

	def add_stat(self, stat: StatModel):
		self.stats.append(stat)

	@property
	def perfection(self) -> float:
		if not self.stats:
			return 0.0
		total_perfection = sum(stat.perfection for stat in self.stats)
		return total_perfection / len(self.stats)

	def __repr__(self):
		return f"(Total Perf: {self.perfection:.2f}%, Stats: {self.stats})"