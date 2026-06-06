#updated 2026-06-03
from __future__ import annotations
from .enums import Rarity
from ..random_pcg import RandomPCG

class SummonLevelConfig:
	def __init__(self, data: dict) -> None:
		self.summons_required:	int   = data.get("SummonsRequired")
		self.common:			float = data.get("Common")
		self.rare:				float = data.get("Rare")
		self.epic:				float = data.get("Epic")
		self.legendary:			float = data.get("Legendary")
		self.ultimate:			float = data.get("Ultimate")
		self.mythic:			float = data.get("Mythic")

	def get_chances(self) -> dict[Rarity, float]:
		return {
			Rarity.Common:		self.common,
			Rarity.Rare:		self.rare,
			Rarity.Epic:		self.epic,
			Rarity.Legendary:	self.legendary,
			Rarity.Ultimate:	self.ultimate,
			Rarity.Mythic:		self.mythic,
		}

	def roll_rarity(self, rng: RandomPCG) -> Rarity:
		roll = rng.next_f64()
		accumulated = 0.0
		for rarity, chance in self.get_chances().items():
			if chance <= 0.0:
				continue
			accumulated += chance
			if roll < accumulated:
				return rarity
		return Rarity.Common
