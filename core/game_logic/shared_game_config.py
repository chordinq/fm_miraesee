from __future__ import annotations
from typing import Any
import ast
from dataclasses import dataclass

from .enums import (
	AscendableType,
	CombatSkill,
	ItemAge,
	ItemType,
	PetBalancingType,
	Rarity,
	SecondaryStatType,
	StatNature,
	StatType,
	TechTreeNodeType,
	TechTreeType,
)
from .player.player_equipment_model import ItemId
from .player.player_mount_collection_model import MountId
from .player.player_pet_collection_model import PetId
from .stats import Stats, UniqueStat
from .stats.skill_stats import SkillStats
from .stats.stat_target import (
	ActiveSkillStatTarget,
	MountStatTarget,
	PassiveSkillStatTarget,
	PetStatTarget,
)
from .stats.stat_helper import StatHelper
from .summon_config import SummonConfig

type GameConfigLibrary[TKey, TInfo] = dict[TKey, TInfo]


@dataclass(frozen=True)
class ForgeConfig:
	forge_cost: int
	free_forge_upgrades: int
	forge_gem_skip_cost_per_second: float
	tech_tree_gem_skip_cost_per_second: float
	pet_gem_skip_cost_per_second: float

	@classmethod
	def from_dict(cls, data: dict) -> ForgeConfig:
		return cls(
			forge_cost=int(data.get("ForgeCost", 1)),
			free_forge_upgrades=int(data.get("FreeForgeUpgrades", 0)),
			forge_gem_skip_cost_per_second=float(data.get("ForgeGemSkipCostPerSecond", 0.0)),
			tech_tree_gem_skip_cost_per_second=float(data.get("TechTreeGemSkipCostPerSecond", 0.0)),
			pet_gem_skip_cost_per_second=float(data.get("PetGemSkipCostPerSecond", 0.0)),
		)


@dataclass(frozen=True)
class ItemBalancingConfig:
	"""C# ItemBalancingConfig — global combat/power scaling."""

	level_scaling_base: float
	sell_base_price: float
	player_melee_damage_multiplier: float
	player_base_damage: float
	player_base_health: float
	enemy_ranged_damage_multiplier: float
	player_power_damage_multiplier: float
	player_base_crit_damage: float
	item_base_max_level: float

	@classmethod
	def from_dict(cls, data: dict) -> ItemBalancingConfig:
		return cls(
			level_scaling_base=float(data.get("LevelScalingBase", 1.0)),
			sell_base_price=float(data.get("SellBasePrice", 0.0)),
			player_melee_damage_multiplier=float(data.get("PlayerMeleeDamageMultiplier", 1.0)),
			player_base_damage=float(data.get("PlayerBaseDamage", 0.0)),
			player_base_health=float(data.get("PlayerBaseHealth", 0.0)),
			enemy_ranged_damage_multiplier=float(data.get("EnemyRangedDamageMultiplier", 1.0)),
			player_power_damage_multiplier=float(data.get("PlayerPowerDamageMultiplier", 1.0)),
			player_base_crit_damage=float(data.get("PlayerBaseCritDamage", 0.0)),
			item_base_max_level=float(data.get("ItemBaseMaxLevel", 0.0)),
		)


@dataclass(frozen=True)
class SkillBaseConfig:
	skills_count: int
	skill_slots_count: int

	@classmethod
	def from_dict(cls, data: dict) -> SkillBaseConfig:
		return cls(
			skills_count=int(data.get("SkillsCount", 0)),
			skill_slots_count=int(data.get("SkillSlotsCount", 0)),
		)


@dataclass(frozen=True)
class PetBaseConfig:
	pet_slots_count: int
	egg_hatch_slot_start_count: int
	egg_hatch_slot_max_count: int
	egg_hatch_slot_three_cost: int
	egg_hatch_slot_four_cost: int

	@classmethod
	def from_dict(cls, data: dict) -> PetBaseConfig:
		return cls(
			pet_slots_count=int(data.get("PetSlotsCount", 0)),
			egg_hatch_slot_start_count=int(data.get("EggHatchSlotStartCount", 0)),
			egg_hatch_slot_max_count=int(data.get("EggHatchSlotMaxCount", 0)),
			egg_hatch_slot_three_cost=int(data.get("EggHatchSlotThreeCost", 0)),
			egg_hatch_slot_four_cost=int(data.get("EggHatchSlotFourCost", 0)),
		)

def _enum_value(enum_cls: type, raw: Any):
	if isinstance(raw, str):
		return enum_cls[raw]
	return enum_cls(int(raw))


def parse_item_id_key(key: str | dict) -> ItemId:
	if isinstance(key, dict):
		return ItemId(
			_enum_value(ItemAge, key["Age"]),
			_enum_value(ItemType, key["Type"]),
			int(key["Idx"]),
		)
	if isinstance(key, str) and key.startswith("{"):
		return parse_item_id_key(ast.literal_eval(key))
	raise ValueError(f"Cannot parse ItemId key: {key!r}")


def parse_item_id_from_row(row: dict) -> ItemId:
	item_id = row.get("ItemId", row)
	return parse_item_id_key(item_id)


def build_item_library(raw: dict) -> GameConfigLibrary[ItemId, dict]:
	out: GameConfigLibrary[ItemId, dict] = {}
	for key, value in raw.items():
		try:
			item_id = parse_item_id_key(key)
		except (ValueError, SyntaxError):
			if "ItemId" not in value:
				continue
			try:
				item_id = parse_item_id_from_row(value)
			except (ValueError, SyntaxError, KeyError):
				continue
		out[item_id] = value
	return out


def build_pet_library(raw: dict) -> GameConfigLibrary[PetId, dict]:
	out: GameConfigLibrary[PetId, dict] = {}
	for _key, value in raw.items():
		pid = value.get("PetId", value)
		pet_id = PetId(
			Rarity[pid["Rarity"]] if isinstance(pid["Rarity"], str) else Rarity(int(pid["Rarity"])),
			int(pid["Id"]),
		)
		out[pet_id] = value
	return out


def build_mount_library(raw: dict) -> GameConfigLibrary[MountId, dict]:
	out: GameConfigLibrary[MountId, dict] = {}
	for _key, value in raw.items():
		mid = value.get("MountId", value)
		mount_id = MountId(
			Rarity[mid["Rarity"]] if isinstance(mid["Rarity"], str) else Rarity(int(mid["Rarity"])),
			int(mid["Id"]),
		)
		out[mount_id] = value
	return out


def build_skill_library(raw: dict) -> GameConfigLibrary[CombatSkill, dict]:
	out: GameConfigLibrary[CombatSkill, dict] = {}
	for _key, value in raw.items():
		skill_type = value.get("Type")
		if skill_type is None:
			continue
		try:
			skill = CombatSkill[skill_type] if isinstance(skill_type, str) else CombatSkill(int(skill_type))
		except (KeyError, ValueError):
			continue
		out[skill] = value
	return out


def build_secondary_stat_library(raw: dict) -> GameConfigLibrary[SecondaryStatType, dict]:
	return {SecondaryStatType[name]: data for name, data in raw.items()}


def build_stat_config_library(raw: dict) -> GameConfigLibrary[tuple[StatType, StatNature], dict]:
	out: GameConfigLibrary[tuple[StatType, StatNature], dict] = {}
	for _key, row in raw.items():
		unique = row["UniqueStat"]
		st = StatType[unique["StatType"]]
		sn = StatNature[unique["StatNature"]]
		out[(st, sn)] = row
	return out


def build_tech_tree_library(raw: dict) -> GameConfigLibrary[TechTreeNodeType, dict]:
	return {TechTreeNodeType[name]: data for name, data in raw.items()}


def build_ascension_library(raw: dict) -> GameConfigLibrary[AscendableType, dict]:
	return {AscendableType[name]: data for name, data in raw.items()}


@dataclass
class SharedGameConfig:
	base_config: dict
	forge_config: ForgeConfig
	item_balancing_config: ItemBalancingConfig
	skill_base_config: SkillBaseConfig
	pet_base_config: PetBaseConfig

	egg_summon_config: SummonConfig
	mount_summon_config: SummonConfig
	skill_summon_config: SummonConfig

	secondary_stat_library: GameConfigLibrary[SecondaryStatType, dict]
	secondary_stat_item_unlock_library: dict[int, dict]
	secondary_stat_pet_unlock_library: GameConfigLibrary[Rarity, dict]
	stat_config_library: GameConfigLibrary[tuple[StatType, StatNature], dict]

	item_balancing_library: dict
	items: GameConfigLibrary[ItemId, dict]
	weapons: GameConfigLibrary[ItemId, dict]
	item_age_drop_chances_library: dict[int, dict]
	item_level_brackets_library: dict[int, dict]
	forge_upgrade_library: dict[int, dict]

	skill_library: GameConfigLibrary[CombatSkill, dict]
	skill_upgrade_library: GameConfigLibrary[int, dict]
	skill_passive_library: GameConfigLibrary[Rarity, dict]

	pet_library: GameConfigLibrary[PetId, dict]
	pet_upgrade_library: GameConfigLibrary[Rarity, dict]
	pet_balancing_library: GameConfigLibrary[PetBalancingType, dict]
	egg_library: GameConfigLibrary[Rarity, dict]

	mount_library: GameConfigLibrary[MountId, dict]
	mount_upgrade_library: GameConfigLibrary[Rarity, dict]

	tech_tree_library: GameConfigLibrary[TechTreeNodeType, dict]
	tech_tree_position_library: GameConfigLibrary[TechTreeType, dict]
	tech_tree_upgrade_library: dict[int, dict]

	ascension_configs_library: GameConfigLibrary[AscendableType, dict]

	player_segments_library: dict[str, dict]
	unlock_conditions_library: dict[str, dict]

	@classmethod
	def load(cls) -> SharedGameConfig:
		import config as cfg
		from .enums import AscendableType

		return cls(
			base_config=cfg.BASE_CONFIG,
			forge_config=ForgeConfig.from_dict(cfg.FORGE_CONFIG),
			item_balancing_config=ItemBalancingConfig.from_dict(cfg.ITEM_BALANCING_CONFIG),
			skill_base_config=SkillBaseConfig.from_dict(cfg.SKILL_BASE_CONFIG),
			pet_base_config=PetBaseConfig.from_dict(cfg.PET_BASE_CONFIG),
			egg_summon_config=SummonConfig(AscendableType.Pets),
			mount_summon_config=SummonConfig(AscendableType.Mounts),
			skill_summon_config=SummonConfig(AscendableType.Skills),
			secondary_stat_library=build_secondary_stat_library(cfg.SECONDARY_STAT_LIBRARY),
			secondary_stat_item_unlock_library={
				int(k): v for k, v in cfg.SECONDARY_STAT_ITEM_UNLOCK_LIBRARY.items()
			},
			secondary_stat_pet_unlock_library={
				Rarity[k]: v for k, v in cfg.SECONDARY_STAT_PET_UNLOCK_LIBRARY.items()
			},
			stat_config_library=build_stat_config_library(cfg.STAT_CONFIG_LIBRARY),
			item_balancing_library=cfg.ITEM_BALANCING_LIBRARY,
			items=build_item_library(cfg.ITEM_BALANCING_LIBRARY),
			weapons=build_item_library(cfg.WEAPON_LIBRARY),
			item_age_drop_chances_library={
				int(k): v for k, v in cfg.ITEM_AGE_DROP_CHANCES_LIBRARY.items()
			},
			item_level_brackets_library={
				int(k): v for k, v in cfg.ITEM_LEVEL_BRACKETS_LIBRARY.items()
			},
			forge_upgrade_library={int(k): v for k, v in cfg.FORGE_UPGRADE_LIBRARY.items()},
			skill_library=build_skill_library(cfg.SKILL_LIBRARY),
			skill_upgrade_library={int(k): v for k, v in cfg.SKILL_UPGRADE_LIBRARY.items()},
			skill_passive_library={
				Rarity[k]: v for k, v in cfg.SKILL_PASSIVE_LIBRARY.items()
			},
			pet_library=build_pet_library(cfg.PET_LIBRARY),
			pet_upgrade_library={Rarity[k]: v for k, v in cfg.PET_UPGRADE_LIBRARY.items()},
			pet_balancing_library={
				PetBalancingType[k]: v for k, v in cfg.PET_BALANCING_LIBRARY.items()
			},
			egg_library={Rarity[k]: v for k, v in cfg.EGG_LIBRARY.items()},
			mount_library=build_mount_library(cfg.MOUNT_LIBRARY),
			mount_upgrade_library={Rarity[k]: v for k, v in cfg.MOUNT_UPGRADE_LIBRARY.items()},
			tech_tree_library=build_tech_tree_library(cfg.TECH_TREE_LIBRARY),
			tech_tree_position_library={
				TechTreeType[k]: v for k, v in cfg.TECH_TREE_POSITION_LIBRARY.items()
			},
			tech_tree_upgrade_library={int(k): v for k, v in cfg.TECH_TREE_UPGRADE_LIBRARY.items()},
			ascension_configs_library=build_ascension_library(cfg.ASCENSION_CONFIGS_LIBRARY),
			player_segments_library=cfg.PLAYER_SEGMENTS,
			unlock_conditions_library=cfg.UNLOCK_CONDITIONS,
		)


def _get_skill_rarity(game_config: SharedGameConfig, combat_skill: CombatSkill) -> Rarity:
	"""IL: SharedGameConfigExtensions.GetRarity — looks up a skill's rarity via skill_library."""
	skill_config = game_config.skill_library.get(combat_skill)
	if skill_config is None:
		raise ValueError(f"Skill not found in skill_library: {combat_skill!r}")
	return Rarity[skill_config["Rarity"]]


def get_resolved_passive_skill_stats(
	game_config: SharedGameConfig,
	combat_skill: CombatSkill,
	level: int,
	total_stats: Stats,
) -> Stats:
	"""IL: SharedGameConfigExtensions.GetResolvedPassiveSkillStats

	Iterates the rarity-based passive skill level stat contributions,
	applies CalculateValueFromStats with a PassiveSkillStatTarget(combat_skill),
	and returns a Stats object ready to be merged into the player's total stats.
	"""
	rarity = _get_skill_rarity(game_config, combat_skill)
	passive_config = game_config.skill_passive_library.get(rarity)
	if passive_config is None:
		raise ValueError(f"No passive skill config for rarity: {rarity!r}")

	level_stats_list = passive_config.get("LevelStats", [])
	if level >= len(level_stats_list):
		return Stats()

	stat_contributions = level_stats_list[level].get("Stats", [])
	target = PassiveSkillStatTarget(skill_type=combat_skill)
	result = Stats()

	for row in stat_contributions:
		stat_node = StatHelper.parse_stat_node(row["StatNode"])
		stat_type = stat_node.unique_stat.stat_type
		value = float(row["Value"])
		calculated = StatHelper.calculate_value_from_stats(
			game_config, total_stats, stat_type, target, value, is_ranged=None
		)
		result.add_stat_contribution(stat_node, calculated)

	return result


def get_resolved_pet_stats(
	game_config: SharedGameConfig,
	pet_id: Any,
	level: int,
	total_stats: Stats,
) -> Stats:
	"""IL: SharedGameConfigExtensions.GetResolvedPetStats

	For each stat row in the pet's level entry, multiplies the row value by the
	pet's balancing multiplier (DamageMultiplier/HealthMultiplier from
	PetBalancingLibrary), then applies CalculateValueFromStats with a
	PetStatTarget(pet_rarity).
	"""
	upgrade_config = game_config.pet_upgrade_library.get(pet_id.rarity)
	if upgrade_config is None:
		raise ValueError(f"No pet upgrade config for rarity: {pet_id.rarity!r}")

	level_info = upgrade_config.get("LevelInfo", [])
	if level >= len(level_info):
		raise IndexError(f"Pet level {level} out of range (max {len(level_info) - 1})")

	stat_rows = level_info[level].get("PetStats", {}).get("Stats", [])

	# Resolve PetBalancingConfig (DamageMultiplier / HealthMultiplier)
	pet_config = game_config.pet_library.get(pet_id)
	balancing: dict | None = None
	if pet_config is not None:
		balance_type = PetBalancingType[pet_config["Type"]]
		balancing = game_config.pet_balancing_library.get(balance_type)

	target = PetStatTarget(pet_rarity=pet_id.rarity)
	result = Stats()

	for row in stat_rows:
		stat_node = StatHelper.parse_stat_node(row["StatNode"])
		stat_type = stat_node.unique_stat.stat_type

		# IL: if no balancing → FD6.One; Health → HealthMultiplier; Damage → DamageMultiplier
		if balancing is None:
			base = 1.0
		elif stat_type == StatType.Health:
			base = float(balancing.get("HealthMultiplier", 1.0))
		elif stat_type == StatType.Damage:
			base = float(balancing.get("DamageMultiplier", 1.0))
		else:
			base = 1.0

		value = float(row["Value"]) * base
		calculated = StatHelper.calculate_value_from_stats(
			game_config, total_stats, stat_type, target, value, is_ranged=None
		)
		result.add_stat_contribution(stat_node, calculated)

	return result


def get_resolved_mount_stats(
	game_config: SharedGameConfig,
	mount_id: Any,
	level: int,
	total_stats: Stats,
) -> Stats:
	"""IL: SharedGameConfigExtensions.GetResolvedMountStats

	Unlike pets there is no balancing multiplier — stat row values are used
	directly as the incoming value to CalculateValueFromStats with a
	MountStatTarget(mount_rarity).
	"""
	upgrade_config = game_config.mount_upgrade_library.get(mount_id.rarity)
	if upgrade_config is None:
		raise ValueError(f"No mount upgrade config for rarity: {mount_id.rarity!r}")

	level_info = upgrade_config.get("LevelInfo", [])
	if level >= len(level_info):
		raise IndexError(f"Mount level {level} out of range (max {len(level_info) - 1})")

	stat_rows = level_info[level].get("MountStats", {}).get("Stats", [])
	target = MountStatTarget(mount_rarity=mount_id.rarity)
	result = Stats()

	for row in stat_rows:
		stat_node = StatHelper.parse_stat_node(row["StatNode"])
		stat_type = stat_node.unique_stat.stat_type
		value = float(row["Value"])
		calculated = StatHelper.calculate_value_from_stats(
			game_config, total_stats, stat_type, target, value, is_ranged=None
		)
		result.add_stat_contribution(stat_node, calculated)

	return result


def get_base_active_skill_stats(
	game_config: SharedGameConfig,
	combat_skill: CombatSkill,
	level: int,
) -> SkillStats:
	"""IL: SharedGameConfigExtensions.GetBaseActiveSkillStats

	Library: skill_library (config+0xf0, TryGetValue by CombatSkill).
	Stat nodes: ActiveSkillStatTarget(combatSkill) — NOT PlayerStatTarget.
	Level bound: len(DamagePerLevel/HealthPerLevel); returns empty SkillStats when OOB.
	"""
	skill_config = game_config.skill_library.get(combat_skill)
	if skill_config is None:
		return SkillStats()

	target = ActiveSkillStatTarget(skill_type=combat_skill)
	_FD6_SCALE = 1_000_000
	result = SkillStats()

	damage_levels = skill_config.get("DamagePerLevel", [])
	if level < len(damage_levels) and damage_levels[level]:
		node = StatHelper.new_additive_stat_node(StatType.Damage, target)
		result.stats[node] = round(float(damage_levels[level]) * _FD6_SCALE)

	health_levels = skill_config.get("HealthPerLevel", [])
	if level < len(health_levels) and health_levels[level]:
		node = StatHelper.new_additive_stat_node(StatType.Health, target)
		result.stats[node] = round(float(health_levels[level]) * _FD6_SCALE)

	return result


def get_resolved_active_skill_stats(
	game_config: SharedGameConfig,
	combat_skill: CombatSkill,
	level: int,
	total_stats: Stats,
) -> Stats:
	"""IL: SharedGameConfigExtensions.GetResolvedActiveSkillStats

	Iterates GetBaseActiveSkillStats contributions (MetaDictionary<StatNode, FD6>),
	applies CalculateValueFromStats with ActiveSkillStatTarget(combat_skill), and
	returns the resolved Stats.
	"""
	result = Stats()
	base = get_base_active_skill_stats(game_config, combat_skill, level)

	for stat_node, raw_fd6 in base.stats.items():
		if raw_fd6 == 0:
			continue
		stat_type = stat_node.unique_stat.stat_type
		target = ActiveSkillStatTarget(skill_type=combat_skill)
		incoming = raw_fd6 / 1_000_000
		calculated = StatHelper.calculate_value_from_stats(
			game_config, total_stats, stat_type, target, incoming, is_ranged=None
		)
		result.add_stat_contribution(stat_node, calculated)

	return result


# ── Utility helpers ───────────────────────────────────────────────────────────


def get_max_skill_count(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.GetMaxSkillCount — SkillBaseConfig.SkillsCount."""
	return game_config.skill_base_config.skills_count


def get_pet_max_level(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.GetPetMaxLevel — max Level across Common PetUpgrade entries."""
	config = game_config.pet_upgrade_library.get(Rarity.Common)
	if config is None:
		return 0
	level_info = config.get("LevelInfo", [])
	if not level_info:
		return 0
	return max(int(entry.get("Level", 0)) for entry in level_info)


def get_mount_max_level(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.GetMountMaxLevel — max Level across Common MountUpgrade entries."""
	config = game_config.mount_upgrade_library.get(Rarity.Common)
	if config is None:
		return 0
	level_info = config.get("LevelInfo", [])
	if not level_info:
		return 0
	return max(int(entry.get("Level", 0)) for entry in level_info)


def max_forge_level(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.MaxForgeLevel — max key in forge_upgrade_library."""
	if not game_config.forge_upgrade_library:
		return 0
	return max(game_config.forge_upgrade_library.keys())


def get_skill_shard_count_to_upgrade(game_config: SharedGameConfig, current_level: int) -> int:
	"""IL: SharedGameConfigExtensions.GetSkillShardCountToUpgrade(config, currentLevel).

	Looks up SkillUpgradeLibrary[currentLevel + 1].Shards.
	Returns -1 if the next level is not found (already maxed).
	"""
	entry = game_config.skill_upgrade_library.get(current_level + 1)
	if entry is None:
		return -1
	return int(entry.get("Shards", -1))


# ── Slot unlock counts ────────────────────────────────────────────────────────
# Full IL: iterates Features.SkillSlots / Features.PetSlots (static C# lists),
# looks up each PlayerSegmentId in player_segments_library, and calls
# IsAgeGateUnlocked(condition, player) which checks battle progress.
# Simplified: counts how many SkillSlot* / PetSlot* segments exist in the
# player_segments_library (i.e. always returns the total configured slot count).
# For a full implementation, add battle-progress tracking to PlayerModel and
# check {DifficultyIdx, AgeIdx, BattleIdx} per slot condition.

_SKILL_SLOT_PREFIX = "SkillSlot"
_PET_SLOT_PREFIX = "PetSlot"


def get_unlocked_skill_slot_count(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.GetUnlockedSkillSlotCount (simplified).

	Returns the total number of SkillSlot* entries in UnlockConditions.
	Real implementation requires player battle-progress tracking.
	"""
	return sum(
		1 for key in game_config.unlock_conditions_library if key.startswith(_SKILL_SLOT_PREFIX)
	)


def get_unlocked_pet_slot_count(game_config: SharedGameConfig) -> int:
	"""IL: SharedGameConfigExtensions.GetUnlockedPetSlotCount (simplified).

	Returns the total number of PetSlot* entries in UnlockConditions.
	Real implementation requires player battle-progress tracking.
	"""
	return sum(
		1 for key in game_config.unlock_conditions_library if key.startswith(_PET_SLOT_PREFIX)
	)


SharedGameConfig.get_resolved_passive_skill_stats = staticmethod(
	get_resolved_passive_skill_stats
)
SharedGameConfig.get_resolved_pet_stats = staticmethod(get_resolved_pet_stats)
SharedGameConfig.get_resolved_mount_stats = staticmethod(get_resolved_mount_stats)
SharedGameConfig.get_base_active_skill_stats = staticmethod(get_base_active_skill_stats)
SharedGameConfig.get_resolved_active_skill_stats = staticmethod(get_resolved_active_skill_stats)
SharedGameConfig.get_max_skill_count = staticmethod(get_max_skill_count)
SharedGameConfig.get_pet_max_level = staticmethod(get_pet_max_level)
SharedGameConfig.get_mount_max_level = staticmethod(get_mount_max_level)
SharedGameConfig.max_forge_level = staticmethod(max_forge_level)
SharedGameConfig.get_skill_shard_count_to_upgrade = staticmethod(get_skill_shard_count_to_upgrade)
SharedGameConfig.get_unlocked_skill_slot_count = staticmethod(get_unlocked_skill_slot_count)
SharedGameConfig.get_unlocked_pet_slot_count = staticmethod(get_unlocked_pet_slot_count)


_default: SharedGameConfig | None = None


def get_shared_game_config() -> SharedGameConfig:
	global _default
	if _default is None:
		_default = SharedGameConfig.load()
	return _default
