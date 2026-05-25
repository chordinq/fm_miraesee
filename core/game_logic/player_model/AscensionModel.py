# models/AscensionModel.py
from core.enums import AscendableType, AscensionLevel

class AscensionModel:
	def __init__(self, ascendable_type: AscendableType, current_level: int = AscensionLevel.None_):
		self.ascendable_type = ascendable_type
		self.current_level = current_level

	def inc(self, amount: int = 1) -> int:
		self.current_level += amount
		if self.current_level > AscensionLevel.Apex:
			self.current_level = AscensionLevel.Apex
		return self.current_level

	def dec(self, amount: int = 1) -> int:
		self.current_level -= amount
		if self.current_level < AscensionLevel.None_:
			self.current_level = AscensionLevel.None_
		return self.current_level