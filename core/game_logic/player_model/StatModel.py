# models/StatModel.py
from core.enums import SecondaryStatType
from configs import STAT_RANGES

class StatModel:
	def __init__(self, stat_type: SecondaryStatType, perfection: float):
		self.stat_type = stat_type
		self.perfection = perfection 
	
	@property
	def value(self) -> float:
		if not self.perfection:
			return 0.0
		
		ranges = STAT_RANGES.get(self.stat_type.name)
		if not ranges:
			return 0.0
			
		return ranges["lower"] + (self.perfection * (ranges["upper"] - ranges["lower"]))

	def __repr__(self):
		return f"[{self.stat_type.name}: {self.perfection:.2f}%]"