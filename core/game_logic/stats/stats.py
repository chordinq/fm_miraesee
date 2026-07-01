from __future__ import annotations
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Iterable, Mapping
from ..enums import (
	SecondaryStatType,
	StatCondition,
	StatLayer,
	StatNature,
	StatType,
)
from .stat_calc import StatCalcContext
from .stat_target import StatTarget, StatTargetBase

if TYPE_CHECKING:
	from ..config.shared_game_config import SharedGameConfig


@dataclass(frozen=True)
class UniqueStat:
	stat_type: StatType
	stat_nature: StatNature


class StatNode:
	def __init__(
		self,
		unique_stat: UniqueStat,
		target: StatTarget | StatTargetBase,
		layer: StatLayer = StatLayer.None_,
		condition: StatCondition = StatCondition.None_,
		legacy_target: StatTargetBase | None = None,
	) -> None:
		self.unique_stat = unique_stat
		if isinstance(target, StatTargetBase):
			self.legacy_target = legacy_target or target
			converted, leg_layer, leg_cond = StatTarget.from_legacy(target)
			self.target = converted
			self.layer = layer if layer != StatLayer.None_ else leg_layer
			self.condition = (
				condition if condition != StatCondition.None_ else leg_cond
			)
		else:
			self.target = target
			self.layer = StatLayer(layer)
			self.condition = StatCondition(condition)
			self.legacy_target = legacy_target

	@property
	def stat_target(self) -> StatTargetBase:
		if self.legacy_target is not None:
			return self.legacy_target
		raise AttributeError("StatNode.stat_target is only available for legacy nodes")

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, StatNode):
			return False
		return (
			self.unique_stat == other.unique_stat
			and self.target.equals(other.target)
			and self.legacy_target == other.legacy_target
			and self.layer == other.layer
			and self.condition == other.condition
		)

	def __hash__(self) -> int:
		return hash(
			(
				self.unique_stat,
				self.target,
				self.legacy_target,
				self.layer,
				self.condition,
			)
		)


@dataclass
class StatContribution:
	node: StatNode
	raw: int

	def __init__(self, node: StatNode, value: float, *, raw: int | None = None) -> None:
		from core.metaplaymath.fd6 import fd6_from_double

		self.node = node
		self.raw = fd6_from_double(value) if raw is None else raw

	@property
	def value(self) -> float:
		from core.metaplaymath.fd6 import fd6_to_double

		return fd6_to_double(self.raw)


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


def _coerce_lookup_target(target: StatTarget | StatTargetBase) -> StatTarget:
	if isinstance(target, StatTarget):
		return target
	converted, _, _ = StatTarget.from_legacy(target)
	return converted


def _lookup_node_key(
	stat_type: StatType,
	nature: StatNature,
	target: StatTarget | StatTargetBase,
) -> StatNode:
	return StatNode(
		UniqueStat(stat_type, nature),
		_coerce_lookup_target(target),
		StatLayer.None_,
		StatCondition.None_,
	)


class Stats:
	def __init__(
		self,
		stat_contributions: Mapping[StatNode, float | int] | None = None,
		*,
		other: Stats | None = None,
	) -> None:
		self.all_stat_contributions: dict[StatNode, int] = {}
		self.total_secondary_stats: dict[SecondaryStatType, float] = {}
		if stat_contributions is not None:
			self.add_stat_contributions(stat_contributions)
		if other is not None:
			self.add_stat_contributions(other)

	def add_stat_contribution(self, node: StatNode, value: float) -> None:
		from core.metaplaymath.fd6 import fd6_from_double

		self.add_stat_contribution_fd6_raw(node, fd6_from_double(value))

	def add_stat_contribution_fd6_raw(self, node: StatNode, raw: int) -> None:
		from core.metaplaymath.fd6 import fd6_add_raw

		if node not in self.all_stat_contributions:
			self.all_stat_contributions[node] = raw
			return
		self.all_stat_contributions[node] = fd6_add_raw(
			self.all_stat_contributions[node], raw
		)

	def contribution_fd6_to_double(self, node: StatNode) -> float | None:
		from core.metaplaymath.fd6 import fd6_to_double

		raw = self.all_stat_contributions.get(node)
		if raw is None:
			return None
		return fd6_to_double(raw)

	def iter_stat_contributions_double(self):
		from core.metaplaymath.fd6 import fd6_to_double

		for node, raw in self.all_stat_contributions.items():
			yield node, fd6_to_double(raw)

	def add_stat_contribution_row(self, contribution: StatContribution) -> None:
		self.add_stat_contribution_fd6_raw(contribution.node, contribution.raw)

	def add_stat_contributions(
		self,
		contributions: (
			Mapping[StatNode, float | int]
			| Stats
			| list[StatContribution]
			| "SecondaryStats"
			| StatContributions
		),
		game_config: SharedGameConfig | None = None,
	) -> None:
		if isinstance(contributions, Stats):
			self._merge_stats(contributions)
			return
		from .secondary_stats import SecondaryStats
		from .skill_stats import SkillStats

		if isinstance(contributions, SkillStats):
			for node, raw in contributions.stats.items():
				self.add_stat_contribution_fd6_raw(node, raw)
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
			if isinstance(value, int):
				self.add_stat_contribution_fd6_raw(node, value)
			else:
				self.add_stat_contribution(node, float(value))

	def _merge_stats(self, other: Stats) -> None:
		for node, raw in other.all_stat_contributions.items():
			self.add_stat_contribution_fd6_raw(node, raw)
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

	def without_secondary_stats(self, game_config: SharedGameConfig) -> Stats:
		"""IL: Stats.WithoutSecondaryStats — Stats(other) then RemoveSecondaryStatContributions."""
		result = Stats(other=self)
		result.remove_secondary_stat_contributions(game_config)
		return result

	def remove_secondary_stat_contributions(
		self,
		game_config: SharedGameConfig,
	) -> None:
		"""IL: Stats.RemoveSecondaryStatContributions."""
		from core.metaplaymath.fd6 import fd6_from_double, fd6_sub_raw

		from .stat_helper import StatHelper

		for sec_type, sec_value in list(self.total_secondary_stats.items()):
			nodes = StatHelper.get_secondary_affected_nodes(sec_type, game_config)
			sec_raw = fd6_from_double(sec_value)
			for node in nodes:
				if node not in self.all_stat_contributions:
					continue
				adjusted = fd6_sub_raw(self.all_stat_contributions[node], sec_raw)
				if adjusted == 0:
					del self.all_stat_contributions[node]
				else:
					self.all_stat_contributions[node] = adjusted
		self.total_secondary_stats.clear()

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

	@staticmethod
	def _nature_fallback_default_fd6_raw(nature: StatNature) -> int:
		"""IL: GetStatValueOrDefault config-miss → FD6.Zero / FD6.One by nature."""
		from core.metaplaymath.fd6 import fd6_from_int

		if nature in (StatNature.Additive, StatNature.OneMinusMultiplier):
			return fd6_from_int(0)
		return fd6_from_int(1)

	def _lookup_stat_config_row(
		self,
		game_config: SharedGameConfig | None,
		stat_type: StatType,
		nature: StatNature,
	) -> tuple[bool, dict | None]:
		if game_config is None:
			return False, None
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
		from core.metaplaymath.fd6 import fd6_to_double

		return fd6_to_double(
			self.get_stat_default_value_fd6_raw(game_config, stat_type, nature)
		)

	def get_stat_default_value_fd6_raw(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
	) -> int:
		from core.metaplaymath.config_values import stat_config_default_fd6_raw

		found, row = self._lookup_stat_config_row(game_config, stat_type, nature)
		if found and row is not None:
			return stat_config_default_fd6_raw(row)
		return self._nature_fallback_default_fd6_raw(nature)

	def get_stat_value_or_default(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
		target: StatTarget | StatTargetBase,
	) -> float:
		from core.metaplaymath.fd6 import fd6_to_double

		return fd6_to_double(
			self.get_stat_value_or_default_fd6_raw(
				game_config, stat_type, nature, target
			)
		)

	def get_stat_value_or_default_fd6_raw(
		self,
		game_config: SharedGameConfig,
		stat_type: StatType,
		nature: StatNature,
		target: StatTarget | StatTargetBase,
	) -> int:
		"""IL: Stats.GetStatValueOrDefault → FD6 (default + contribution)."""
		from core.metaplaymath.fd6 import fd6_add_raw

		default_raw = self.get_stat_default_value_fd6_raw(game_config, stat_type, nature)
		node = _lookup_node_key(stat_type, nature, target)
		contribution = self.all_stat_contributions.get(node)
		if contribution is not None:
			return fd6_add_raw(default_raw, contribution)
		return default_raw

	def get_stat_value_or_default_unique(
		self,
		game_config: SharedGameConfig,
		unique_stat: UniqueStat,
		target: StatTarget | StatTargetBase,
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
		target: StatTarget | StatTargetBase,
	) -> tuple[bool, float]:
		from core.metaplaymath.fd6 import fd6_add_raw, fd6_to_double

		default_raw = self.get_stat_default_value_fd6_raw(game_config, stat_type, nature)
		node = _lookup_node_key(stat_type, nature, target)
		contribution = self.all_stat_contributions.get(node)
		if contribution is not None:
			return True, fd6_to_double(fd6_add_raw(default_raw, contribution))
		return False, fd6_to_double(default_raw)

	def player_damage(
		self,
		game_config: SharedGameConfig,
		is_ranged: bool,
	) -> float:
		"""IL: Stats.PlayerDamage — Damage(0), StatTarget.Player, incoming FD6.Zero, isRanged context."""
		from .stat_helper import StatHelper
		from .stat_target import StatTarget

		return StatHelper.calculate_value_from_stats(
			game_config,
			self,
			StatType.Damage,
			StatTarget.player(),
			0.0,
			StatCalcContext(is_ranged),
		)

	def player_health(self, game_config: SharedGameConfig) -> float:
		"""IL: Stats.PlayerHealth — Health(1), StatTarget.Player, incoming FD6.Zero, no context."""
		from .stat_helper import StatHelper
		from .stat_target import StatTarget

		return StatHelper.calculate_value_from_stats(
			game_config,
			self,
			StatType.Health,
			StatTarget.player(),
			0.0,
			StatCalcContext(None),
		)
