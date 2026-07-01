#updated 2026-06-03
from __future__ import annotations

from core.metaplaymath.config_values import config_f64_raw
from core.metaplaymath.f64 import f64_add_raw, f64_from_raw, f64_less_than_raw

from ..enums import Rarity
from ...random_pcg import RandomPCG


class SummonLevelConfig:
	def __init__(self, data: dict) -> None:
		self.summons_required: int = data.get("SummonsRequired")
		self.common: float = data.get("Common")
		self.rare: float = data.get("Rare")
		self.epic: float = data.get("Epic")
		self.legendary: float = data.get("Legendary")
		self.ultimate: float = data.get("Ultimate")
		self.mythic: float = data.get("Mythic")
		self._chances_f64_raw: dict[Rarity, int] = {
			Rarity.Common: config_f64_raw(self.common),
			Rarity.Rare: config_f64_raw(self.rare),
			Rarity.Epic: config_f64_raw(self.epic),
			Rarity.Legendary: config_f64_raw(self.legendary),
			Rarity.Ultimate: config_f64_raw(self.ultimate),
			Rarity.Mythic: config_f64_raw(self.mythic),
		}

	def get_chances(self) -> dict[Rarity, float]:
		return {
			rarity: f64_from_raw(raw)
			for rarity, raw in self._chances_f64_raw.items()
		}

	def roll_rarity(self, rng: RandomPCG) -> Rarity:
		"""IL: SummonLevelConfig.RollRarity — NextF64 cumulative F64 compare."""
		roll_raw = rng.next_f64_raw()
		accumulated = 0
		for rarity, chance_raw in self._chances_f64_raw.items():
			if chance_raw <= 0:
				continue
			accumulated = f64_add_raw(accumulated, chance_raw)
			if f64_less_than_raw(roll_raw, accumulated):
				return rarity
		return Rarity.Common
