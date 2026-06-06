from __future__ import annotations
from typing import Mapping
from .stats import StatContribution, StatNode

_FD6_SCALE = 1_000_000

class SkillStats:
	def __init__(self, stats: list[StatContribution] | None = None) -> None:
		self.stats: dict[StatNode, int] = {}
		if stats is not None:
			for contribution in stats:
				self.stats[contribution.node] = round(float(contribution.value) * _FD6_SCALE)

	def add_to_contributions(self, other: SkillStats | Mapping[StatNode, int]) -> None:
		if isinstance(other, SkillStats):
			other = other.stats
		for node, value in other.items():
			if node not in self.stats:
				self.stats[node] = value
			else:
				self.stats[node] = self.stats[node] + value
