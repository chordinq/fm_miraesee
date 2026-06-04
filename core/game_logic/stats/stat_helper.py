from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Optional, Sequence, TypeVar

from ..enums import *
from ..random_pcg import RandomPCG
from ..stat_target import *
from .stats import *

T = TypeVar("T")


def _optional_enum(enum_cls: type, raw: Any):
	if raw is None:
		return None
	if isinstance(raw, str):
		return enum_cls[raw]
	return enum_cls(int(raw))


@dataclass
class _NatureAccumulators:
	additive: float
	multiplier: float
	divisor: float
	one_minus: float


# C# IL uses stat types 0x13/0x15 (Damage) and 0x14/0x16 (Health) — mapped to tech/ascension here
_DAMAGE_DEPENDENCY_TYPES = (StatType.TechTreeDamage, StatType.AscensionDamage)
_HEALTH_DEPENDENCY_TYPES = (StatType.TechTreeHealth, StatType.AscensionHealth)


class StatHelper:
	@staticmethod
	def parse_unique_stat(data: dict) -> UniqueStat:
		block = data.get("UniqueStat", data)
		st = block["StatType"]
		sn = block["StatNature"]
		return UniqueStat(
			StatType[st] if isinstance(st, str) else StatType(int(st)),
			StatNature[sn] if isinstance(sn, str) else StatNature(int(sn)),
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
		block = data.get("StatNode", data)
		return StatNode(
			StatHelper.parse_unique_stat(block),
			StatHelper.parse_stat_target(block["StatTarget"]),
		)

	@staticmethod
	def parse_stat_contribution_row(row: dict) -> StatContribution:
		return StatContribution(
			StatHelper.parse_stat_node(row["StatNode"]),
			float(row.get("Value", 0.0)),
		)

	@staticmethod
	def new_additive_stat_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Additive), stat_target)

	@staticmethod
	def new_multiplicative_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Multiplier), stat_target)

	@staticmethod
	def new_divisor_node(stat_type: StatType, stat_target: StatTargetBase) -> StatNode:
		return StatNode(UniqueStat(stat_type, StatNature.Divisor), stat_target)

	@staticmethod
	def sum_f64(values: Iterable[float]) -> float:
		return sum(values)

	@staticmethod
	def sum_fd6(values: Iterable[float]) -> float:
		return sum(values)

	@staticmethod
	def sum_uint128(values: Iterable[int]) -> int:
		return sum(values)

	@staticmethod
	def sum_mapped(values: Iterable[T], selector: Callable[[T], int]) -> int:
		return sum(selector(v) for v in values)

	@staticmethod
	def get_secondary_affected_nodes(
		secondary_type: SecondaryStatType,
		game_config: Any,
	) -> list[StatNode]:
		if game_config is not None:
			row = game_config.secondary_stat_library.get(secondary_type)
			if row is not None:
				return [
					StatHelper.parse_stat_node(n)
					for n in row.get("StatNodes", [])
				]
		from config import SECONDARY_STAT_LIBRARY

		raw = SECONDARY_STAT_LIBRARY.get(secondary_type.name)
		if raw is None:
			return []
		return [StatHelper.parse_stat_node(n) for n in raw.get("StatNodes", [])]

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
			result.stats.append(StatContribution(spec.stat_node, value))
		return result

	@staticmethod
	def calculate_value(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		incoming_value: float | int,
	) -> float:
		game_config = StatHelper._player_game_config(player)
		stats = StatHelper._player_total_stats(player)
		is_ranged = getattr(player, "is_ranged", None)
		return StatHelper.calculate_value_from_stats(
			game_config,
			stats,
			stat_type,
			target_base,
			float(incoming_value),
			is_ranged,
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
		acc = _NatureAccumulators(
			additive=stats_to_use.get_stat_value_or_default(
				game_config, stat_type, StatNature.Additive, target_base
			),
			multiplier=stats_to_use.get_stat_value_or_default(
				game_config, stat_type, StatNature.Multiplier, target_base
			),
			divisor=stats_to_use.get_stat_value_or_default(
				game_config, stat_type, StatNature.Divisor, target_base
			),
			one_minus=stats_to_use.get_stat_value_or_default(
				game_config, stat_type, StatNature.OneMinusMultiplier, target_base
			),
		)

		StatHelper._add_dependency_contributions(
			game_config,
			stats_to_use,
			stat_type,
			target_base,
			acc,
			is_ranged,
		)

		result = float(incoming_value) + acc.additive
		result *= acc.multiplier
		result *= 1.0 - acc.one_minus
		if acc.divisor != 0.0:
			result /= acc.divisor
		return result

	@staticmethod
	def roll_stat(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		random: RandomPCG,
	) -> bool:
		game_config = StatHelper._player_game_config(player)
		stats = StatHelper._player_total_stats(player)
		chance = stats.get_stat_value_or_default(
			game_config, stat_type, StatNature.Multiplier, target_base
		)
		return random.next_f64() < chance

	@staticmethod
	def roll_from_custom_stats(
		player: Any,
		stat_type: StatType,
		target_base: StatTargetBase,
		random: RandomPCG,
	) -> bool:
		raise NotImplementedError("RollFromCustomStats — deferred")

	@staticmethod
	def _merge_try_get_into_accumulators(
		stats: Stats,
		game_config: Any,
		stat_type: StatType,
		target: StatTargetBase,
		acc: _NatureAccumulators,
	) -> None:
		found, value = stats.try_get_stat_value(
			game_config, stat_type, StatNature.Additive, target
		)
		if found:
			acc.additive += value

		found, value = stats.try_get_stat_value(
			game_config, stat_type, StatNature.Multiplier, target
		)
		if found:
			acc.multiplier *= value

		found, value = stats.try_get_stat_value(
			game_config, stat_type, StatNature.Divisor, target
		)
		if found:
			acc.divisor *= value

		found, value = stats.try_get_stat_value(
			game_config, stat_type, StatNature.OneMinusMultiplier, target
		)
		if found:
			acc.one_minus += value

	@staticmethod
	def _add_dependency_contributions(
		game_config: Any,
		stats: Stats,
		stat_type: StatType,
		target: StatTargetBase,
		acc: _NatureAccumulators,
		is_ranged: Optional[bool],
	) -> None:
		StatHelper._merge_try_get_into_accumulators(
			stats, game_config, stat_type, target, acc
		)

		if stat_type == StatType.Health:
			for dep in _HEALTH_DEPENDENCY_TYPES:
				StatHelper._add_dependency_contributions(
					game_config, stats, dep, target, acc, is_ranged
				)
		elif stat_type == StatType.Damage:
			for dep in _DAMAGE_DEPENDENCY_TYPES:
				StatHelper._add_dependency_contributions(
					game_config, stats, dep, target, acc, is_ranged
				)

		StatHelper._add_dependency_for_target(
			game_config, stats, stat_type, target, acc, is_ranged
		)

	@staticmethod
	def _add_dependency_for_target(
		game_config: Any,
		stats: Stats,
		stat_type: StatType,
		target: StatTargetBase,
		acc: _NatureAccumulators,
		is_ranged: Optional[bool],
	) -> None:
		if isinstance(target, PlayerStatTarget) and is_ranged is not None:
			alt = (
				PlayerRangedOnlyStatTarget()
				if is_ranged
				else PlayerMeleeOnlyStatTarget()
			)
			StatHelper._add_dependency_contributions(
				game_config, stats, stat_type, alt, acc, is_ranged
			)
			StatHelper._add_dependency_contributions(
				game_config,
				stats,
				stat_type,
				PlayerSkinMultiplierStatTarget(),
				acc,
				is_ranged,
			)

	@staticmethod
	def _player_game_config(player: Any) -> Any:
		cfg = getattr(player, "game_config", None)
		if cfg is not None:
			return cfg
		from ..shared_game_config import get_shared_game_config

		return get_shared_game_config()

	@staticmethod
	def _player_total_stats(player: Any) -> Stats:
		getter = getattr(player, "get_total_stats", None)
		if callable(getter):
			return getter()
		total = getattr(player, "total_stats", None)
		if isinstance(total, Stats):
			return total
		return Stats()
