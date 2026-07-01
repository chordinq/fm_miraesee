from __future__ import annotations

"""JSON / MPC config scalar → IL F64/FD6 raw (boundary parsing + SGC normalization)."""

from typing import Any

from core.metaplaymath.f64 import f64_to_raw
from core.metaplaymath.fd6 import fd6_from_double
from core.metaplaymath.types import F64Raw, FD6Raw

_DEFAULT_VALUE_FD6_KEY = "DefaultValueFd6Raw"
_VALUE_FD6_KEY = "ValueFd6Raw"
_LOWER_F64_KEY = "LowerRangeF64Raw"
_UPPER_F64_KEY = "UpperRangeF64Raw"
_DAMAGE_PER_LEVEL_FD6_KEY = "DamagePerLevelFd6Raw"
_HEALTH_PER_LEVEL_FD6_KEY = "HealthPerLevelFd6Raw"
_VALUE_INCREASE_FD6_KEY = "ValueIncreaseFd6Raw"


def config_f64_raw(value: float | int) -> F64Raw:
	"""IL: F64.FromDouble on config JSON scalars."""
	return f64_to_raw(float(value))


def config_fd6_raw(value: float | int) -> FD6Raw:
	"""IL: FD6.FromDouble / op_Implicit on config JSON scalars."""
	return fd6_from_double(float(value))


def stat_config_default_fd6_raw(row: dict) -> FD6Raw:
	if _DEFAULT_VALUE_FD6_KEY in row:
		return row[_DEFAULT_VALUE_FD6_KEY]
	return config_fd6_raw(row["DefaultValue"])


def stat_contribution_value_fd6_raw(row: dict) -> FD6Raw:
	if _VALUE_FD6_KEY in row:
		return row[_VALUE_FD6_KEY]
	return config_fd6_raw(row.get("Value", 0.0))


def stat_contribution_value_increase_fd6_raw(row: dict) -> FD6Raw:
	if _VALUE_INCREASE_FD6_KEY in row:
		return row[_VALUE_INCREASE_FD6_KEY]
	return config_fd6_raw(row.get("ValueIncrease", 0.0))


def secondary_stat_lower_f64_raw(row: dict) -> F64Raw:
	if _LOWER_F64_KEY in row:
		return row[_LOWER_F64_KEY]
	return config_f64_raw(row["LowerRange"])


def secondary_stat_upper_f64_raw(row: dict) -> F64Raw:
	if _UPPER_F64_KEY in row:
		return row[_UPPER_F64_KEY]
	return config_f64_raw(row["UpperRange"])


def normalize_stat_config_row(row: dict) -> None:
	if _DEFAULT_VALUE_FD6_KEY not in row and "DefaultValue" in row:
		row[_DEFAULT_VALUE_FD6_KEY] = config_fd6_raw(row["DefaultValue"])


def normalize_stat_contribution_row(row: dict) -> None:
	if _VALUE_FD6_KEY not in row and "Value" in row:
		row[_VALUE_FD6_KEY] = config_fd6_raw(row.get("Value", 0.0))
	if _VALUE_INCREASE_FD6_KEY not in row and "ValueIncrease" in row:
		row[_VALUE_INCREASE_FD6_KEY] = config_fd6_raw(row.get("ValueIncrease", 0.0))


def normalize_tech_tree_entry(entry: dict) -> None:
	normalize_stat_contribution_rows(entry.get("Stats"))


def normalize_secondary_stat_row(row: dict) -> None:
	if _LOWER_F64_KEY not in row and "LowerRange" in row:
		row[_LOWER_F64_KEY] = config_f64_raw(row["LowerRange"])
	if _UPPER_F64_KEY not in row and "UpperRange" in row:
		row[_UPPER_F64_KEY] = config_f64_raw(row["UpperRange"])


def normalize_stat_contribution_rows(rows: list[dict] | None) -> None:
	if not rows:
		return
	for row in rows:
		if isinstance(row, dict):
			normalize_stat_contribution_row(row)


def normalize_level_stats_entries(entries: list[dict] | None) -> None:
	if not entries:
		return
	for entry in entries:
		normalize_stat_contribution_rows(entry.get("Stats"))


def normalize_pet_upgrade_config(config: dict) -> None:
	for level_info in config.get("LevelInfo", []):
		normalize_stat_contribution_rows(
			level_info.get("PetStats", {}).get("Stats")
		)


def normalize_mount_upgrade_config(config: dict) -> None:
	for level_info in config.get("LevelInfo", []):
		normalize_stat_contribution_rows(
			level_info.get("MountStats", {}).get("Stats")
		)


def normalize_skill_passive_config(config: dict) -> None:
	normalize_level_stats_entries(config.get("LevelStats"))


def normalize_ascension_config(config: dict) -> None:
	for level_cfg in config.get("AscensionConfigPerLevel", []):
		normalize_stat_contribution_rows(level_cfg.get("StatContributions"))


def normalize_sets_tier(tier: dict) -> None:
	normalize_stat_contribution_rows(tier.get("BonusStats", {}).get("Stats"))


def normalize_equipment_info(info: dict) -> None:
	rows = info.get("EquipmentStats")
	if rows is None:
		rows = info.get("Stats")
	normalize_stat_contribution_rows(list(rows or []))


def normalize_skill_config(skill_config: dict) -> None:
	for key, fd6_key in (
		("DamagePerLevel", _DAMAGE_PER_LEVEL_FD6_KEY),
		("HealthPerLevel", _HEALTH_PER_LEVEL_FD6_KEY),
	):
		if fd6_key in skill_config:
			continue
		levels = skill_config.get(key)
		if levels is None:
			continue
		skill_config[fd6_key] = [config_fd6_raw(v) for v in levels]


def skill_level_fd6_raw(skill_config: dict, key: str, level: int) -> int | None:
	fd6_key = {
		"DamagePerLevel": _DAMAGE_PER_LEVEL_FD6_KEY,
		"HealthPerLevel": _HEALTH_PER_LEVEL_FD6_KEY,
	}.get(key)
	if fd6_key is not None and fd6_key in skill_config:
		levels = skill_config[fd6_key]
		if level < len(levels):
			return levels[level]
		return None
	levels = skill_config.get(key, [])
	if level < len(levels) and levels[level]:
		return config_fd6_raw(levels[level])
	return None


def normalize_rarity_library(
	library: dict[Any, dict],
	*,
	per_entry: Any,
) -> dict[Any, dict]:
	for config in library.values():
		per_entry(config)
	return library
