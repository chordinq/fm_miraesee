from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Iterable, Optional, Sequence, TypeVar

from .enums import (
	AttackType,
	CombatSkill,
	CurrencyType,
	DungeonType,
	ItemType,
	Rarity,
	SecondaryStatType,
	StatNature,
	StatType,
)
from .random_pcg import RandomPCG, U32_DENOM
from .secondary_stats import SecondaryStats
from .stat_target import (
	ActiveSkillStatTarget,
	CurrencyBonusStatTarget,
	DungeonStatTarget,
	EggStatTarget,
	EquipmentStatTarget,
	ForgeStatTarget,
	MountStatTarget,
	OfflineCurrencyStatTarget,
	OfflineTimerStatTarget,
	PassiveSkillStatTarget,
	PetStatTarget,
	PlayerMeleeOnlyStatTarget,
	PlayerRangedOnlyStatTarget,
	PlayerSkinMultiplierStatTarget,
	PlayerStatTarget,
	StatTargetBase,
	TechTreeStatTarget,
	WeaponStatTarget,
)
from .stats import StatContribution, StatNode, Stats, UniqueStat

T = TypeVar("T")

_default_values_cache: dict[tuple[StatType, StatNature], float] | None = None
_secondary_nodes_cache: dict[SecondaryStatType, list[StatNode]] | None = None


def _optional_enum(enum_cls: type, raw: Any):
	if raw is None:
		return None
	if isinstance(raw, str):
		return enum_cls[raw]
	return enum_cls(int(raw))


class StatHelper:
	"""Game.Logic.StatHelper — static extension methods on player / stats / config."""

	# ------------------------------------------------------------------
	# Config / parsing (SharedGameConfig + JSON rows)
	# ------------------------------------------------------------------

	@staticmethod
	def default_value(stat_type: StatType, nature: StatNature) -> float:
		global _default_values_cache
		if _default_values_cache is None:
			from config import STAT_CONFIG_LIBRARY

			_default_values_cache = {}
			for _key, row in STAT_CONFIG_LIBRARY.items():
				unique = row["UniqueStat"]
				st = StatType[unique["StatType"]]
				sn = StatNature[unique["StatNature"]]
				_default_values_cache[(st, sn)] = float(row["DefaultValue"])
		return _default_values_cache.get((stat_type, nature), 0.0)

	@staticmethod
	def parse_unique_stat(data: dict) -> UniqueStat:
		block = data.get("UniqueStat", data)
		return UniqueStat(
			StatType[block["StatType"]],
			StatNature[block["StatNature"]],
		)

	@staticmethod
	def parse_stat_target(data: dict) -> StatTargetBase:
		type_name = data.get("$type")
		if type_name == "PlayerStatTarget":
			return PlayerStatTarget()
		if type_name == "PlayerRangedOnlyStatTarget":
			return PlayerRangedOnlyStatTarget()
		if type_name == "PlayerMeleeOnlyStatTarget":
			return PlayerMeleeOnlyStatTarget()
		if type_name == "PlayerSkinMultiplierStatTarget":
			return PlayerSkinMultiplierStatTarget()
		if type_name == "WeaponStatTarget":
			return WeaponStatTarget(_optional_enum(AttackType, data.get("AttackType")))
		if type_name == "EquipmentStatTarget":
			return EquipmentStatTarget(_optional_enum(ItemType, data.get("ItemType")))
		if type_name == "ActiveSkillStatTarget":
			return ActiveSkillStatTarget(_optional_enum(CombatSkill, data.get("SkillType")))
		if type_name == "PassiveSkillStatTarget":
			return PassiveSkillStatTarget(_optional_enum(CombatSkill, data.get("SkillType")))
		if type_name == "MountStatTarget":
			return MountStatTarget(_optional_enum(Rarity, data.get("MountRarity") or data.get("Rarity")))
		if type_name == "PetStatTarget":
			return PetStatTarget(_optional_enum(Rarity, data.get("PetRarity") or data.get("Rarity")))
		if type_name == "EggStatTarget":
			return EggStatTarget(_optional_enum(Rarity, data.get("EggRarity") or data.get("Rarity")))
		if type_name == "ForgeStatTarget":
			return ForgeStatTarget()
		if type_name == "CurrencyBonusStatTarget":
			return CurrencyBonusStatTarget(_optional_enum(CurrencyType, data.get("CurrencyType")))
		if type_name == "OfflineTimerStatTarget":
			return OfflineTimerStatTarget()
		if type_name == "OfflineCurrencyStatTarget":
			return OfflineCurrencyStatTarget(_optional_enum(CurrencyType, data.get("CurrencyType")))
		if type_name == "DungeonStatTarget":
			return DungeonStatTarget(
				_optional_enum(DungeonType, data.get("DungeonType")),
				_optional_enum(CurrencyType, data.get("CurrencyType")),
			)
		if type_name == "TechTreeStatTarget":
			return TechTreeStatTarget()
		raise ValueError(f"Unknown StatTarget $type: {type_name!r}")

	@staticmethod
	def parse_stat_node(data: dict) -> StatNode:
		return StatNode(
			StatHelper.parse_unique_stat(data),
			StatHelper.parse_stat_target(data["StatTarget"]),
		)

	@staticmethod
	def parse_stat_contribution_row(row: dict) -> StatContribution:
		return StatContribution(
			StatHelper.parse_stat_node(row["StatNode"]),
			float(row.get("Value", 0.0)),
		)

	# ------------------------------------------------------------------
	# StatNode factories (New*StatNode)
	# ------------------------------------------------------------------

	@staticmethod
	def new_additive_stat_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Additive), stat_target)

	@staticmethod
	def new_multiplicative_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Multiplier), stat_target)

	@staticmethod
	def new_divisor_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Divisor), stat_target)

	# ------------------------------------------------------------------
	# Sum helpers
	# ------------------------------------------------------------------

	@staticmethod
	def sum_float(values: Iterable[float]) -> float:
		return sum(values)

	@staticmethod
	def sum_int(values: Iterable[int]) -> int:
		return sum(values)

	@staticmethod
	def sum_mapped(values: Iterable[T], selector) -> int:
		return sum(selector(v) for v in values)

	# ------------------------------------------------------------------
	# Secondary stat → StatNode mapping
	# ------------------------------------------------------------------

	@staticmethod
	def get_secondary_affected_nodes(
		secondary_type: SecondaryStatType,
		game_config: Any = None,
	) -> list[StatNode]:
		global _secondary_nodes_cache
		if _secondary_nodes_cache is None:
			from config import SECONDARY_STAT_LIBRARY

			_secondary_nodes_cache = {}
			for name, data in SECONDARY_STAT_LIBRARY.items():
				sec = SecondaryStatType[name]
				nodes = [StatHelper.parse_stat_node(n) for n in data.get("StatNodes", [])]
				_secondary_nodes_cache[sec] = nodes
		return list(_secondary_nodes_cache.get(secondary_type, []))

	@staticmethod
	def generate_stats_from_range(
		game_config: Any,
		random: RandomPCG,
		stats_to_add: list[RandomValueStatContribution],
	) -> StatContributions:
		result = StatContributions()
		for spec in stats_to_add:
			roll = random.next_f64()
			value = spec.min_value + roll * (spec.max_value - spec.min_value)
			result.add(StatContribution(spec.stat_node, value))
		return result

	# ------------------------------------------------------------------
	# CalculateValue pipeline
	# ------------------------------------------------------------------

	@staticmethod
	def calculate_value(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		incoming_value: float | int,
	) -> float:
		stats = StatHelper._player_total_stats(player)
		return StatHelper.calculate_value_from_stats(
			game_config=None,
			stats_to_use=stats,
			stat_type=stat_type,
			target_base=target_base,
			incoming_value=float(incoming_value),
			is_ranged=None,
		)

	@staticmethod
	def calculate_value_from_stats(
		game_config: Any,
		stats_to_use: Stats,
		stat_type: StatType,
		target_base: StatTargetBase,
		incoming_value: float,
		is_ranged: Optional[bool] = None,
	) -> float:
		buckets: dict[StatNature, list[float]] = {
			StatNature.Multiplier: [],
			StatNature.Additive: [],
			StatNature.Divisor: [],
			StatNature.OneMinusMultiplier: [],
		}

		for node, value in stats_to_use.all_stat_contributions.items():
			if node.unique_stat.stat_type != stat_type:
				continue
			if not StatHelper._target_applies(node.stat_target, target_base, is_ranged):
				continue
			buckets[node.unique_stat.stat_nature].append(value)

		StatHelper._add_dependency_contributions(
			stats_to_use, stat_type, target_base, is_ranged, buckets
		)

		result = float(incoming_value)
		result = StatHelper._apply_nature_bucket(
			result, StatNature.Multiplier, buckets[StatNature.Multiplier], stat_type
		)
		result = StatHelper._apply_nature_bucket(
			result, StatNature.Additive, buckets[StatNature.Additive], stat_type
		)
		result = StatHelper._apply_nature_bucket(
			result, StatNature.Divisor, buckets[StatNature.Divisor], stat_type
		)
		result = StatHelper._apply_nature_bucket(
			result, StatNature.OneMinusMultiplier,
			buckets[StatNature.OneMinusMultiplier],
			stat_type,
		)
		return result

	@staticmethod
	def roll_stat(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		random: RandomPCG,
	) -> bool:
		chance = StatHelper.calculate_value(player, stat_type, target_base, 0.0)
		threshold = int(round(chance * U32_DENOM))
		if threshold <= 0:
			return False
		return random._next_pcg32() < threshold

	@staticmethod
	def roll_from_custom_stats(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		random: RandomPCG,
	) -> bool:
		stats = StatHelper._player_custom_stats(player)
		chance = StatHelper.calculate_value_from_stats(
			None, stats, stat_type, target_base, 0.0, None
		)
		threshold = int(round(chance * U32_DENOM))
		if threshold <= 0:
			return False
		return random._next_pcg32() < threshold

	# ------------------------------------------------------------------
	# Ingest helpers (config rows → Stats)
	# ------------------------------------------------------------------

	@staticmethod
	def ingest_contribution_rows(stats: Stats, rows: Iterable[dict]) -> None:
		for row in rows:
			stats.add_stat_contribution_object(StatHelper.parse_stat_contribution_row(row))

	@staticmethod
	def ingest_secondary_stats(stats: Stats, secondary: SecondaryStats) -> None:
		for sec_type in SecondaryStatType:
			found, value = secondary.try_get_stat_value(sec_type)
			if found:
				stats.add_secondary_stat_contribution(sec_type, value)

	@staticmethod
	def combine_by_nature(values: Sequence[float], nature: StatNature, default: float) -> float:
		if not values:
			return default
		if nature == StatNature.Multiplier:
			result = 1.0
			for v in values:
				result *= v
			return result
		if nature == StatNature.Additive:
			return default + sum(values)
		if nature == StatNature.Divisor:
			result = default if default else 1.0
			for v in values:
				if v == 0:
					continue
				result /= v
			return result
		if nature == StatNature.OneMinusMultiplier:
			result = 1.0
			for v in values:
				result *= (1.0 - v)
			return result
		return default

	# ------------------------------------------------------------------
	# Internal
	# ------------------------------------------------------------------

	@staticmethod
	def _player_total_stats(player: Any) -> Stats:
		"""PlayerModelItemExtensions.GetTotalStats — aggregate when submodels expose Stats."""
		total = Stats()
		# TODO: merge forge / equipment / skills / pets / mounts / techtree contributions
		return total

	@staticmethod
	def _player_custom_stats(player: Any) -> Stats:
		"""Stats used by RollFromCustomStats (equipment-only or similar)."""
		return Stats()

	@staticmethod
	def _target_applies(
		node_target: StatTargetBase,
		query_target: StatTargetBase,
		is_ranged: Optional[bool],
	) -> bool:
		if node_target == query_target:
			return True
		if isinstance(node_target, PlayerStatTarget):
			return isinstance(
				query_target,
				(
					PlayerStatTarget,
					PlayerRangedOnlyStatTarget,
					PlayerMeleeOnlyStatTarget,
					PlayerSkinMultiplierStatTarget,
				),
			)
		if isinstance(node_target, PlayerRangedOnlyStatTarget):
			return is_ranged is True and isinstance(
				query_target, (PlayerStatTarget, PlayerRangedOnlyStatTarget)
			)
		if isinstance(node_target, PlayerMeleeOnlyStatTarget):
			return is_ranged is False and isinstance(
				query_target, (PlayerStatTarget, PlayerMeleeOnlyStatTarget)
			)
		if isinstance(node_target, EquipmentStatTarget) and isinstance(
			query_target, EquipmentStatTarget
		):
			nt, qt = node_target.item_type, query_target.item_type
			return nt is None or qt is None or nt == qt
		if isinstance(node_target, WeaponStatTarget) and isinstance(query_target, WeaponStatTarget):
			nt, qt = node_target.attack_type, query_target.attack_type
			return nt is None or qt is None or nt == qt
		return type(node_target) is type(query_target)

	@staticmethod
	def _add_dependency_contributions(
		stats_to_use: Stats,
		stat_type: StatType,
		target_base: StatTargetBase,
		is_ranged: Optional[bool],
		buckets: dict[StatNature, list[float]],
	) -> None:
		"""CalculateValueFromStats g__AddDependencyContributions — secondary totals → nodes."""
		for sec_type, sec_value in stats_to_use.total_secondary_stats.items():
			for node in StatHelper.get_secondary_affected_nodes(sec_type):
				if node.unique_stat.stat_type != stat_type:
					continue
				if not StatHelper._target_applies(node.stat_target, target_base, is_ranged):
					continue
				buckets[node.unique_stat.stat_nature].append(sec_value)

	@staticmethod
	def _apply_nature_bucket(
		current: float,
		nature: StatNature,
		values: list[float],
		stat_type: StatType,
	) -> float:
		if not values:
			return current
		default = StatHelper.default_value(stat_type, nature)
		combined = StatHelper.combine_by_nature(values, nature, default)
		if nature == StatNature.Multiplier:
			return current * combined
		if nature == StatNature.Additive:
			return current + combined - default
		if nature == StatNature.Divisor:
			return current / combined if combined else current
		if nature == StatNature.OneMinusMultiplier:
			return current * combined
		return current


# --- Types used by StatHelper (Game.Logic) ---


@dataclass
class RandomValueStatContribution:
	"""Config row with MinValue/MaxValue (e.g. skin PossibleStats)."""

	stat_node: StatNode
	min_value: float
	max_value: float

	@classmethod
	def from_dict(cls, data: dict) -> RandomValueStatContribution:
		return cls(
			stat_node=StatHelper.parse_stat_node(data["StatNode"]),
			min_value=float(data["MinValue"]),
			max_value=float(data["MaxValue"]),
		)


@dataclass
class StatContributions:
	"""Bundle of contributions returned by GenerateStatsFromRange."""

	contributions: list[StatContribution] = field(default_factory=list)

	def add(self, contribution: StatContribution) -> None:
		self.contributions.append(contribution)

	def apply_to(self, stats: Stats) -> None:
		for contribution in self.contributions:
			stats.add_stat_contribution_object(contribution)


__all__ = [
	"StatHelper",
	"StatContributions",
	"RandomValueStatContribution",
]
