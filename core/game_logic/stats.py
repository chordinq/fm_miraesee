from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping

from .enums import SecondaryStatType, StatNature, StatType
from .secondary_stats import SecondaryStats
from .stat_target import StatTargetBase


@dataclass(frozen=True)
class UniqueStat:
	stat_type: StatType
	stat_nature: StatNature


@dataclass(frozen=True)
class StatNode:
	unique_stat: UniqueStat
	stat_target: StatTargetBase


@dataclass(frozen=True)
class StatContribution:
	node: StatNode
	value: float


class Stats:
	"""Game.Logic.Stats — primary StatNode contributions + resolved secondary totals."""

	def __init__(self, stat_contributions: Mapping[StatNode, float] | None = None) -> None:
		self.all_stat_contributions: dict[StatNode, float] = dict(stat_contributions or {})
		self.total_secondary_stats: dict[SecondaryStatType, float] = {}

	def add_stat_contribution(self, node: StatNode, value: float) -> None:
		current = self.all_stat_contributions.get(node, 0.0)
		self.all_stat_contributions[node] = current + value

	def add_stat_contributions(self, contributions: Mapping[StatNode, float]) -> None:
		for node, value in contributions.items():
			self.add_stat_contribution(node, value)

	def add_stat_contributions_from_stats(self, other: Stats) -> None:
		self.add_stat_contributions(other.all_stat_contributions)
		for sec_type, sec_value in other.total_secondary_stats.items():
			current = self.total_secondary_stats.get(sec_type, 0.0)
			self.total_secondary_stats[sec_type] = current + sec_value

	def add_stat_contribution_object(self, contribution: StatContribution) -> None:
		self.add_stat_contribution(contribution.node, contribution.value)

	def add_stat_contribution_rows(self, rows: Iterable[dict]) -> None:
		from .stat_helper import StatHelper

		StatHelper.ingest_contribution_rows(self, rows)

	def add_secondary_stat_contribution(
		self,
		secondary_type: SecondaryStatType,
		value: float,
	) -> None:
		current = self.total_secondary_stats.get(secondary_type, 0.0)
		self.total_secondary_stats[secondary_type] = current + value

	def add_secondary_stats(self, secondary: SecondaryStats) -> None:
		from .stat_helper import StatHelper

		StatHelper.ingest_secondary_stats(self, secondary)

	def get_stat_value_or_default(
		self,
		stat_type: StatType,
		nature: StatNature,
		target: StatTargetBase,
	) -> float:
		from .stat_helper import StatHelper

		return StatHelper.get_stat_value_or_default(self, stat_type, nature, target)

	def try_get_stat_value(
		self,
		stat_type: StatType,
		nature: StatNature,
		target: StatTargetBase,
	) -> tuple[bool, float]:
		from .stat_helper import StatHelper

		return StatHelper.try_get_stat_value(self, stat_type, nature, target)
