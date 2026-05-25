# core/game_logic/summon_config/SummonLevelConfig.py
"""
Game.Logic.SummonLevelConfig

Holds per-level summon probabilities and the count required to reach the next level.
Constructed from one entry of the Levels list in a SummonConfig JSON.
"""

from __future__ import annotations

from core.enums import Rarity
from core.random_pcg import RandomPCG


class SummonLevelConfig:
	"""
	Game.Logic.SummonLevelConfig

	Fields mirror the C# backing fields at offsets 0x10 - 0x40:
	  0x10  int   SummonsRequired
	  0x18  F64   Common
	  0x20  F64   Rare
	  0x28  F64   Epic
	  0x30  F64   Legendary
	  0x38  F64   Ultimate
	  0x40  F64   Mythic
	"""

	def __init__(self, data: dict) -> None:
		self.summons_required: int   = data.get("SummonsRequired", 9999)
		self.common:           float = data.get("Common",    0.0)
		self.rare:             float = data.get("Rare",      0.0)
		self.epic:             float = data.get("Epic",      0.0)
		self.legendary:        float = data.get("Legendary", 0.0)
		self.ultimate:         float = data.get("Ultimate",  0.0)
		self.mythic:           float = data.get("Mythic",    0.0)

	# ------------------------------------------------------------------
	# SummonLevelConfig$$GetChances
	# ------------------------------------------------------------------

	def get_chances(self) -> dict[Rarity, float]:
		"""
		SummonLevelConfig$$GetChances -- builds Dictionary<Rarity, F64>.
		Insertion order matches C#: Common(0) -> Rare(1) -> ... -> Mythic(5).
		"""
		return {
			Rarity.Common:    self.common,
			Rarity.Rare:      self.rare,
			Rarity.Epic:      self.epic,
			Rarity.Legendary: self.legendary,
			Rarity.Ultimate:  self.ultimate,
			Rarity.Mythic:    self.mythic,
		}

	# ------------------------------------------------------------------
	# SummonLevelConfig$$RollRarity
	# ------------------------------------------------------------------

	def roll_rarity(self, rng: RandomPCG) -> Rarity:
		"""
		SummonLevelConfig$$RollRarity

		C# uses NextF64 (0.0 - 1.0) then iterates Dictionary<Rarity, F64>
		accumulating probabilities until roll < accumulated sum.
		Consumes exactly 1 PCG call.
		"""
		roll = rng.next_f64()
		accumulated = 0.0
		for rarity, chance in self.get_chances().items():
			if chance <= 0.0:
				continue
			accumulated += chance
			if roll < accumulated:
				return rarity
		return Rarity.Common
