# ui/services/stat_display.py — stat lines for detail panel (pets, items, mounts)
from __future__ import annotations

from dataclasses import dataclass

from configs import PET_MAPPING
from configs.config import (
	PET_BALANCING_LIBRARY,
	PET_UPGRADE_LIBRARY,
	load_json,
)
from core.enums import PetBalancingType, Rarity, SecondaryStatType, StatType
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.player_model.StatModel import StatModel
from core.game_logic.tech_tree_stats import pet_tech_multipliers
from ui.services.display_level import display_level
from ui.services.localization import secondary_stat_display_name, stat_type_display_name

_BALANCING = load_json("configs/parsed_configs/ItemBalancingConfig.json")
_BASE_DAMAGE = float(_BALANCING.get("PlayerBaseDamage", 10.0))
_BASE_HEALTH = float(_BALANCING.get("PlayerBaseHealth", 80.0))
_LEVEL_SCALE = float(_BALANCING.get("LevelScalingBase", 1.01))
# Tuned so DamageMulti / HealthMulti on *items* display in the same ballpark as in-game.
_PRIMARY_DISPLAY_SCALE = 10_000.0

_PRIMARY_STATS = frozenset({"DamageMulti", "HealthMulti"})


def format_compact(value: float) -> str:
	"""Compact stat values with 2 decimal places (e.g. 201.60k, 8.25k)."""
	n = abs(value)
	if n >= 1_000_000:
		return f"{value / 1_000_000:.2f}M"
	if n >= 1_000:
		return f"{value / 1_000:.2f}k"
	return f"{value:.2f}"


def stat_label(stat_type: SecondaryStatType) -> str:
	return secondary_stat_display_name(stat_type)


def _level_multiplier(dump_level: int) -> float:
	return _LEVEL_SCALE ** display_level(dump_level)


def _primary_amount(stat: StatModel, dump_level: int) -> float:
	base = _BASE_DAMAGE if stat.stat_type.name == "DamageMulti" else _BASE_HEALTH
	return base * stat.value * _level_multiplier(dump_level) * _PRIMARY_DISPLAY_SCALE


@dataclass(frozen=True)
class StatLine:
	text: str
	primary: bool  # bold light; else gray bonus line


def _pet_balancing_type(rarity: Rarity, pet_id: int) -> str:
	"""PetBalancingLibrary key (Balanced / Damage / Health) from PetMapping.Type."""
	key = f"{int(rarity)}_{pet_id}"
	entry = PET_MAPPING.get(key, {})
	try:
		return PetBalancingType(int(entry.get("Type", 0))).name
	except ValueError:
		return "Balanced"


def _pet_config_level(dump_level: int) -> int:
	"""
	Map dump-stored level to PetUpgradeLibrary ``Level`` field.

	UI shows dump+1 (Lv.1 when dump=0) → config Level 0.
	"""
	return max(0, int(dump_level))


def _rarity_level_base_stats(rarity: Rarity, dump_level: int) -> tuple[float, float]:
	lib = PET_UPGRADE_LIBRARY.get(rarity.name)
	if not lib:
		return 0.0, 0.0
	config_level = _pet_config_level(dump_level)
	level_info = next(
		(entry for entry in lib["LevelInfo"] if entry["Level"] == config_level),
		lib["LevelInfo"][min(config_level, len(lib["LevelInfo"]) - 1)],
	)
	dmg = hp = 0.0
	for entry in level_info["PetStats"]["Stats"]:
		stat_type = entry["StatNode"]["UniqueStat"]["StatType"]
		value = float(entry["Value"])
		if stat_type == "Damage":
			dmg = value
		elif stat_type == "Health":
			hp = value
	return dmg, hp


def pet_base_damage_health(
	rarity: Rarity,
	pet_id: int,
	*,
	dump_level: int = 0,
	player: PlayerModel | None = None,
) -> tuple[float, float]:
	"""
	PetUpgrade × PetBalancing × tech tree (PetBonusDamage / PetBonusHealth).

	PetBalancingLibrary.json:
	  Balanced — 1.0 / 1.0
	  Damage   — 1.5 damage, 0.5 health
	  Health   — 0.5 damage, 1.5 health
	"""
	pet_type = _pet_balancing_type(rarity, pet_id)
	balancing = PET_BALANCING_LIBRARY.get(pet_type, PET_BALANCING_LIBRARY["Balanced"])
	dmg_mul = float(balancing["DamageMultiplier"])
	hp_mul = float(balancing["HealthMultiplier"])
	base_dmg, base_hp = _rarity_level_base_stats(rarity, dump_level)
	tech_dmg, tech_hp = pet_tech_multipliers(player)
	return base_dmg * dmg_mul * tech_dmg, base_hp * hp_mul * tech_hp


def _bonus_stat_lines(
	stats: SecondaryStatsModel,
	*,
	skip: frozenset[str] | None = None,
) -> list[StatLine]:
	rows: list[StatLine] = []
	excluded = skip or frozenset()
	for stat in stats.stats:
		if stat.stat_type.name in excluded:
			continue
		label = stat_label(stat.stat_type)
		pct = stat.value * 100.0
		rows.append(StatLine(text=f"+{pct:.2f}% {label}", primary=False))
	return rows


def _stat_perfection(stats: SecondaryStatsModel, stat_name: str) -> float | None:
	for stat in stats.stats:
		if stat.stat_type.name == stat_name:
			return stat.value
	return None


def pet_detail_stat_lines(
	rarity: Rarity,
	pet_id: int,
	secondary_stats: SecondaryStatsModel,
	*,
	dump_level: int = 0,
	player: PlayerModel | None = None,
) -> list[StatLine]:
	"""Base Health + Damage (upgrade × balancing × tech), then secondary bonus stats."""
	dmg, hp = pet_base_damage_health(
		rarity, pet_id, dump_level=dump_level, player=player
	)
	rows: list[StatLine] = [
		StatLine(
			text=f"{format_compact(dmg)} {stat_type_display_name(StatType.Damage)}",
			primary=True,
		),
		StatLine(
			text=f"{format_compact(hp)} {stat_type_display_name(StatType.Health)}",
			primary=True,
		),
	]
	# Pets: DamageMulti / HealthMulti are rolled secondaries (not item-style primaries).
	rows.extend(_bonus_stat_lines(secondary_stats))
	return rows


def item_detail_stat_lines(
	secondary_stats: SecondaryStatsModel,
	*,
	dump_level: int = 0,
) -> list[StatLine]:
	"""Equipped item: Health + Damage (DamageMulti / HealthMulti), then bonus % stats."""
	rows: list[StatLine] = []
	hp_val = _stat_perfection(secondary_stats, "HealthMulti")
	if hp_val is not None:
		hp_stat = StatModel(SecondaryStatType.HealthMulti, hp_val)
		rows.append(
			StatLine(
				text=(
					f"{format_compact(_primary_amount(hp_stat, dump_level))} "
					f"{stat_type_display_name(StatType.Health)}"
				),
				primary=True,
			)
		)
	dmg_val = _stat_perfection(secondary_stats, "DamageMulti")
	if dmg_val is not None:
		dmg_stat = StatModel(SecondaryStatType.DamageMulti, dmg_val)
		rows.append(
			StatLine(
				text=(
					f"{format_compact(_primary_amount(dmg_stat, dump_level))} "
					f"{stat_type_display_name(StatType.Damage)}"
				),
				primary=True,
			)
		)
	rows.extend(_bonus_stat_lines(secondary_stats, skip=_PRIMARY_STATS))
	return rows


def stat_lines_for(stats: SecondaryStatsModel, *, dump_level: int = 0) -> list[StatLine]:
	"""Equipment / mount secondary stats (may use compact primary lines for DamageMulti/HealthMulti)."""
	rows: list[StatLine] = []
	for stat in stats.stats:
		label = stat_label(stat.stat_type)
		if stat.stat_type.name in _PRIMARY_STATS:
			amount = _primary_amount(stat, dump_level)
			rows.append(StatLine(text=f"{format_compact(amount)} {label}", primary=True))
		else:
			pct = stat.value * 100.0
			rows.append(StatLine(text=f"+{pct:.2f}% {label}", primary=False))
	return rows
