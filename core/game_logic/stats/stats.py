from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Mapping

from ..enums import SecondaryStatType, StatNature, StatType
from .stat_target import PlayerStatTarget, StatTargetBase
from .secondary_stats import SecondaryStats

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


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


@dataclass
class StatContributions:
	stats: list[StatContribution] = field(default_factory=list)


@dataclass
class RandomValueStatContribution:
	stat_node: StatNode
	min_value: float
	max_value: float

	@classmethod
	def from_dict(cls, data: dict) -> RandomValueStatContribution:
		from .stat_helper import StatHelper

		return cls(
			stat_node=StatHelper.parse_stat_node(data["StatNode"]),
			min_value=float(data["MinValue"]),
			max_value=float(data["MaxValue"]),
		)


class Stats:
	def __init__(
		self,
		stat_contributions: Mapping[StatNode, float] | None = None,
		*,
		other: Stats | None = None,
	) -> None:
		self.all_stat_contributions: dict[StatNode, float] = {}
		self.total_secondary_stats: dict[SecondaryStatType, float] = {}
		if stat_contributions is not None:
			self.add_stat_contributions(stat_contributions)
		if other is not None:
			self.add_stat_contributions(other)

	def add_stat_contribution(self, node: StatNode, value: float) -> None:
		if node not in self.all_stat_contributions:
			self.all_stat_contributions[node] = float(value)
			return
		self.all_stat_contributions[node] += float(value)

	def add_stat_contribution_row(self, contribution: StatContribution) -> None:
		self.add_stat_contribution(contribution.node, contribution.value)

	def add_stat_contributions(
		self,
		contributions: (
			Mapping[StatNode, float]
			| Stats
			| list[StatContribution]
			| SecondaryStats
			| StatContributions
		),
		game_config: SharedGameConfig | None = None,
	) -> None:
		if isinstance(contributions, Stats):
			self._merge_stats(contributions)
			return
		if isinstance(contributions, SecondaryStats):
			if game_config is None:
				raise TypeError("game_config is required when merging SecondaryStats into Stats")
			self._merge_secondary_stats(contributions, game_config)
			return
		if isinstance(contributions, list):
			for row in contributions:
				self.add_stat_contribution_row(row)
			return
		if isinstance(contributions, StatContributions):
			for row in contributions.stats:
				self.add_stat_contribution_row(row)
			return
		for node, value in contributions.items():
			self.add_stat_contribution(node, value)

	def _merge_stats(self, other: Stats) -> None:
		for node, value in other.all_stat_contributions.items():
			self.add_stat_contribution(node, value)
		for sec_type, sec_value in other.total_secondary_stats.items():
			current = self.total_secondary_stats.get(sec_type, 0.0)
			self.total_secondary_stats[sec_type] = current + float(sec_value)

	def add_secondary_stat_contribution(
		self,
		secondary_type: SecondaryStatType,
		value: float,
		related_nodes: Iterable[StatNode] | None = None,
		*,
		game_config: SharedGameConfig | None = None,
	) -> None:
		if related_nodes is None and game_config is not None:
			from .stat_helper import StatHelper

			related_nodes = StatHelper.get_secondary_affected_nodes(
				secondary_type, game_config
			)

		if secondary_type not in self.total_secondary_stats:
			self.total_secondary_stats[secondary_type] = float(value)
		else:
			self.total_secondary_stats[secondary_type] += float(value)

		if related_nodes:
			for node in related_nodes:
				self.add_stat_contribution(node, value)

	def _merge_secondary_stats(
		self,
		secondary: SecondaryStats,
		game_config: SharedGameConfig,
	) -> None:
		from .stat_helper import StatHelper

		library = game_config.secondary_stat_library
		for sec_type in secondary.interpolated_stat_values:
			row = library.get(sec_type)
			if row is None:
				continue
			found, calculated = secondary.try_get_stat_value(sec_type, game_config)
			if not found:
				continue
			raw_nodes = row.get("StatNodes", [])
			nodes = [StatHelper.parse_stat_node(n) for n in raw_nodes]
			self.add_secondary_stat_contribution(
				sec_type, calculated, related_nodes=nodes
			)

	@staticmethod
	def _nature_fallback_default(nature: StatNature) -> float:
		if nature in (StatNature.Additive, StatNature.OneMinusMultiplier):
			return 0.0
		return 1.0

	def _lookup_stat_config_row(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
	) -> tuple[bool, dict | None]:
		row = game_config.stat_config_library.get((stat_type, nature))
		if row is None:
			return False, None
		return True, row

	def get_stat_default_value(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
	) -> float:
		found, row = self._lookup_stat_config_row(game_config, stat_type, nature)
		if found and row is not None:
			return float(row["DefaultValue"])
		return self._nature_fallback_default(nature)

	def get_stat_value_or_default(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
		target: StatTargetBase,
	) -> float:
		found, row = self._lookup_stat_config_row(game_config, stat_type, nature)
		if not found or row is None:
			return self._nature_fallback_default(nature)

		default = float(row["DefaultValue"])
		node = StatNode(UniqueStat(stat_type, nature), target)
		contribution = self.all_stat_contributions.get(node)
		if contribution is not None:
			return default + contribution
		return default

	def get_stat_value_or_default_unique(
		self,
		game_config: SharedGameConfig,
		unique_stat: UniqueStat,
		target: StatTargetBase,
	) -> float:
		return self.get_stat_value_or_default(
			game_config,
			unique_stat.stat_type,
			unique_stat.stat_nature,
			target,
		)

	def try_get_stat_value(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
		target: StatTargetBase,
	) -> tuple[bool, float]:
		default = self.get_stat_default_value(game_config, stat_type, nature)
		node = StatNode(UniqueStat(stat_type, nature), target)
		contribution = self.all_stat_contributions.get(node)
		if contribution is not None:
			return True, default + contribution
		return False, default

	def player_damage(
		self,
		game_config: SharedGameConfig,
		is_ranged: bool,
	) -> float:
		from .stat_helper import StatHelper

		target = PlayerStatTarget()
		return StatHelper.calculate_value_from_stats(
			game_config,
			self,
			StatType.Damage,
			target,
			0.0,
			is_ranged,
		)

	def player_health(self, game_config: SharedGameConfig) -> float:
		from .stat_helper import StatHelper

		target = PlayerStatTarget()
		return StatHelper.calculate_value_from_stats(
			game_config,
			self,
			StatType.Health,
			target,
			0.0,
			False,
		)
