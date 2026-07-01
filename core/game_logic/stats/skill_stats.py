from __future__ import annotations
from typing import Mapping
from .stats import StatContribution, StatNode


class SkillStats:
	def __init__(self, stats: list[StatContribution] | None = None) -> None:
		self.stats: dict[StatNode, int] = {}
		if stats is not None:
			for contribution in stats:
				self.stats[contribution.node] = contribution.raw

	def add_to_contributions(
		self,
		other: "SkillStats | Stats | Mapping[StatNode, int]",
	) -> None:
		from core.metaplaymath.fd6 import fd6_add_raw

		from .stats import Stats

		if isinstance(other, Stats):
			other = other.all_stat_contributions
		elif isinstance(other, SkillStats):
			other = other.stats
		for node, value in other.items():
			if node not in self.stats:
				self.stats[node] = value
			else:
				self.stats[node] = fd6_add_raw(self.stats[node], value)
