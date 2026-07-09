from __future__ import annotations
from typing import Any, Callable, Iterable, Optional, TypeVar
from ..enums import (
	CombatSkill,
	CurrencyType,
	DungeonType,
	ItemType,
	Rarity,
	SecondaryStatType,
	StatCondition,
	StatLayer,
	StatNature,
	StatQualifierType,
	StatTargetKind,
	StatType,
	AttackType,
)
from ...random_pcg import RandomPCG
from .stat_calc import LayerBucket, StatCalcContext
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
	StatQualifier,
	StatTarget,
	StatTargetBase,
	TechTreeStatTarget,
	WeaponStatTarget,
)
from .stats import StatContribution, StatContributions, StatNode, Stats, UniqueStat

T = TypeVar("T")


def _optional_enum(enum_cls: type, raw: Any):
	if raw is None:
		return None
	if isinstance(raw, str):
		return enum_cls[raw]
	return enum_cls(int(raw))


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
	def parse_modern_stat_target(data: dict) -> StatTarget:
		kind = data.get("Kind", data.get("kind"))
		if isinstance(kind, str):
			kind = StatTargetKind[kind]
		else:
			kind = StatTargetKind(int(kind))

		raw_qualifiers = data.get("Qualifiers") or []
		qualifiers: list[StatQualifier] = []
		for row in raw_qualifiers:
			qualifier_type = row.get("Type")
			if isinstance(qualifier_type, str):
				qualifier_type = StatQualifierType[qualifier_type]
			else:
				qualifier_type = StatQualifierType(int(qualifier_type))
			qualifiers.append(StatQualifier(qualifier_type, int(row["Value"])))
		return StatTarget(kind, tuple(qualifiers))

	@staticmethod
	def _parse_stat_layer(raw: object) -> StatLayer:
		if raw is None or raw == "None":
			return StatLayer.None_
		if isinstance(raw, StatLayer):
			return raw
		if isinstance(raw, str):
			return StatLayer["None_" if raw == "None" else raw]
		return StatLayer(int(raw))

	@staticmethod
	def _parse_stat_condition(raw: object) -> StatCondition:
		if raw is None or raw == "None":
			return StatCondition.None_
		if isinstance(raw, StatCondition):
			return raw
		if isinstance(raw, str):
			return StatCondition["None_" if raw == "None" else raw]
		return StatCondition(int(raw))

	@staticmethod
	def parse_stat_node(data: dict) -> StatNode:
		block = data.get("StatNode", data)
		unique_stat = StatHelper.parse_unique_stat(block)

		if block.get("Target") is not None:
			target = StatHelper.parse_modern_stat_target(block["Target"])
			layer = StatHelper._parse_stat_layer(block.get("Layer"))
			condition = StatHelper._parse_stat_condition(block.get("Condition"))
			legacy = None
			if block.get("LegacyTarget") is not None:
				legacy = StatHelper.parse_stat_target(block["LegacyTarget"])
			elif block.get("StatTarget") is not None:
				legacy = StatHelper.parse_stat_target(block["StatTarget"])
			return StatNode(unique_stat, target, layer, condition, legacy)

		if block.get("StatTarget") is not None:
			legacy = StatHelper.parse_stat_target(block["StatTarget"])
			return StatNode(unique_stat, legacy)

		raise ValueError("StatNode payload missing Target/StatTarget")

	@staticmethod
	def parse_stat_contribution_row(row: dict) -> StatContribution:
		from core.metaplaymath.config_values import stat_contribution_value_fd6_raw

		node = StatHelper.parse_stat_node(row["StatNode"])
		raw = stat_contribution_value_fd6_raw(row)
		return StatContribution(node, 0.0, raw=raw)

	@staticmethod
	def _coerce_target(target: StatTarget | StatTargetBase) -> StatTarget:
		if isinstance(target, StatTarget):
			return target
		converted, _, _ = StatTarget.from_legacy(target)
		return converted

	@staticmethod
	def _coerce_context(
		context: StatCalcContext | bool | None,
	) -> StatCalcContext:
		if isinstance(context, StatCalcContext):
			return context
		if context is None:
			return StatCalcContext(None)
		return StatCalcContext(bool(context))

	@staticmethod
	def new_additive_stat_node(
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		layer: StatLayer = StatLayer.None_,
		condition: StatCondition = StatCondition.None_,
	) -> StatNode:
		return StatNode(
			UniqueStat(stat_type, StatNature.Additive),
			target,
			layer,
			condition,
		)

	@staticmethod
	def new_multiplicative_node(
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		layer: StatLayer = StatLayer.None_,
		condition: StatCondition = StatCondition.None_,
	) -> StatNode:
		return StatNode(
			UniqueStat(stat_type, StatNature.Multiplier),
			target,
			layer,
			condition,
		)

	@staticmethod
	def new_divisor_node(
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		layer: StatLayer = StatLayer.None_,
		condition: StatCondition = StatCondition.None_,
	) -> StatNode:
		return StatNode(
			UniqueStat(stat_type, StatNature.Divisor),
			target,
			layer,
			condition,
		)

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
		stats_to_add: list,
	) -> StatContributions:
		"""IL: StatHelper.GenerateStatsFromRange — NextF64InRange per row."""
		result = StatContributions()
		for spec in stats_to_add:
			value = random.next_f64_in_range(spec.min_value, spec.max_value)
			result.stats.append(StatContribution(spec.stat_node, value))
		return result

	@staticmethod
	def gather_contributions(
		stats: Stats,
		stat_type: StatType,
		target: StatTarget,
		context: StatCalcContext,
		layers: dict[StatLayer, LayerBucket],
	) -> None:
		for node, value_raw in stats.all_stat_contributions.items():
			if node.unique_stat.stat_type != stat_type:
				continue
			if not node.target.equals(target):
				continue
			if not context.is_condition_met(node.condition):
				continue
			bucket = layers.get(node.layer)
			if bucket is None:
				bucket = LayerBucket.create()
			bucket.add(node.unique_stat.stat_nature, value_raw)
			layers[node.layer] = bucket

	@staticmethod
	def calculate_value(
		player: Any,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		incoming_value: float | int,
	) -> float:
		game_config = StatHelper._player_game_config(player)
		stats = StatHelper._player_total_stats(player)
		is_ranged = StatHelper._player_is_ranged_optional(player)
		return StatHelper.calculate_value_from_stats(
			game_config,
			stats,
			stat_type,
			target,
			float(incoming_value),
			StatCalcContext(is_ranged),
		)

	@staticmethod
	def calculate_value_round_to_int(
		player: Any,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		incoming_value: float | int,
	) -> int:
		"""IL: StatHelper.CalculateValue + FD6.RoundToInt."""
		game_config = StatHelper._player_game_config(player)
		stats = StatHelper._player_total_stats(player)
		is_ranged = StatHelper._player_is_ranged_optional(player)
		raw = StatHelper.calculate_value_fd6_raw_from_stats(
			game_config,
			stats,
			stat_type,
			target,
			float(incoming_value),
			StatCalcContext(is_ranged),
		)
		from core.metaplaymath.fd6 import fd6_round_to_int

		return fd6_round_to_int(raw)

	@staticmethod
	def calculate_value_from_stats(
		game_config: Any,
		stats_to_use: Stats,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		incoming_value: float,
		context: StatCalcContext | bool | None = None,
	) -> float:
		"""IL: StatHelper.CalculateValueFromStats — FD6 layer pipeline."""
		from core.metaplaymath.fd6 import fd6_to_double

		raw = StatHelper.calculate_value_fd6_raw_from_stats(
			game_config,
			stats_to_use,
			stat_type,
			target,
			incoming_value,
			context,
		)
		return fd6_to_double(raw)

	@staticmethod
	def calculate_value_fd6_raw_from_stats(
		game_config: Any,
		stats_to_use: Stats,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		incoming_value: float,
		context: StatCalcContext | bool | None = None,
	) -> int:
		"""IL: StatHelper.CalculateValueFromStats — returns FD6 raw Int128."""
		from core.metaplaymath.fd6 import (
			fd6_add_raw,
			fd6_div_raw,
			fd6_from_double,
			fd6_from_int,
			fd6_mul_raw,
			fd6_sub_raw,
		)

		fd6_one = fd6_from_int(1)
		resolved_target = StatHelper._coerce_target(target)
		resolved_context = StatHelper._coerce_context(context)
		layers: dict[StatLayer, LayerBucket] = {}

		StatHelper.gather_contributions(
			stats_to_use, stat_type, resolved_target, resolved_context, layers
		)
		for dependency in resolved_target.get_dependencies():
			StatHelper.gather_contributions(
				stats_to_use, stat_type, dependency, resolved_context, layers
			)

		general = layers.get(StatLayer.None_, LayerBucket.create())
		default_multiplier = stats_to_use.get_stat_default_value_fd6_raw(
			game_config, stat_type, StatNature.Multiplier
		)
		default_divisor = stats_to_use.get_stat_default_value_fd6_raw(
			game_config, stat_type, StatNature.Divisor
		)

		value_raw = fd6_add_raw(fd6_from_double(incoming_value), general.additive)
		multiplier_raw = default_multiplier
		if general.has_multiplier:
			multiplier_raw = fd6_add_raw(multiplier_raw, general.multiplier)
		value_raw = fd6_mul_raw(value_raw, multiplier_raw)
		value_raw = fd6_mul_raw(
			value_raw, fd6_sub_raw(fd6_one, general.one_minus_multiplier)
		)
		divisor_raw = default_divisor
		if general.has_divisor:
			divisor_raw = fd6_add_raw(divisor_raw, general.divisor)
		if divisor_raw == 0:
			raise ZeroDivisionError("Stat divisor resolved to zero")
		value_raw = fd6_div_raw(value_raw, divisor_raw)

		for layer, bucket in layers.items():
			if layer == StatLayer.None_:
				continue
			value_raw = fd6_add_raw(value_raw, bucket.additive)
			if bucket.has_multiplier:
				value_raw = fd6_mul_raw(
					value_raw, fd6_add_raw(fd6_one, bucket.multiplier)
				)
			value_raw = fd6_mul_raw(
				value_raw, fd6_sub_raw(fd6_one, bucket.one_minus_multiplier)
			)
			if bucket.has_divisor:
				value_raw = fd6_div_raw(
					value_raw, fd6_add_raw(fd6_one, bucket.divisor)
				)

		return int(value_raw)

	@staticmethod
	def calculate_timer_duration_seconds(
		player: Any,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		base_duration: float,
	) -> int:
		"""IL: StatHelper.CalculateValue + FD6.RoundToInt for TimerModel duration."""
		return round(
			StatHelper.calculate_value(player, stat_type, target, base_duration)
		)

	@staticmethod
	def roll_stat(
		player: Any,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		random: RandomPCG,
	) -> bool:
		"""IL: StatHelper.RollStat — NextFixedD6() < GetStatValueOrDefault(...)."""
		game_config = StatHelper._player_game_config(player)
		stats = StatHelper._player_total_stats(player)
		chance_raw = stats.get_stat_value_or_default_fd6_raw(
			game_config, stat_type, StatNature.Multiplier, target
		)
		return random.compare_fixed_d6_less_than(chance_raw)

	@staticmethod
	def roll_from_custom_stats(
		player: Any,
		stat_type: StatType,
		target: StatTarget | StatTargetBase,
		random: RandomPCG,
	) -> bool:
		return StatHelper.roll_stat(player, stat_type, target, random)

	@staticmethod
	def _player_is_ranged_optional(player: Any) -> Optional[bool]:
		explicit = getattr(player, "is_ranged", None)
		if explicit is not None:
			return bool(explicit)

		equipment = getattr(player, "equipment", None)
		if equipment is None:
			equipment = getattr(player, "player_equipment_model", None)
		if equipment is None:
			return None
		weapon = getattr(equipment, "weapon", None)
		if weapon is None:
			return None

		game_config = StatHelper._player_game_config(player)
		weapons = getattr(game_config, "weapons", None)
		if not weapons:
			return None
		item_id = getattr(weapon, "item_id", None)
		if item_id is None:
			return None
		info = weapons.get(item_id)
		if info is None:
			return None
		return bool(info.get("IsRanged", False))

	@staticmethod
	def _player_game_config(player: Any) -> Any:
		return player.game_config

	@staticmethod
	def _player_total_stats(player: Any) -> Stats:
		from ..player.player_model import get_total_stats
		from ..player.player_model import PlayerModel

		if isinstance(player, PlayerModel):
			return get_total_stats(player)
		total = getattr(player, "total_stats", None)
		if isinstance(total, Stats):
			return total
		return Stats()
