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
from .models.player_equipment_model import ItemId
from .models.player_mount_collection_model import MountId
from .models.player_pet_collection_model import PetId
from .stats import UniqueStat
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
			if "ItemId" in value:
				item_id = parse_item_id_from_row(value)
			else:
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
		out[CombatSkill(int(skill_type))] = value
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
	skill_upgrade_library: dict[int, dict]
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
		)


_default: SharedGameConfig | None = None


def get_shared_game_config() -> SharedGameConfig:
	global _default
	if _default is None:
		_default = SharedGameConfig.load()
	return _default
