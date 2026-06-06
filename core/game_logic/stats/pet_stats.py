from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from ...miraesee_extension import miraesee_extension
from ..enums import (
	AscendableType,
	PetBalancingType,
	Rarity,
	StatNature,
	StatType,
	TechTreeNodeType,
	TechTreeType,
)
from ..player.player_pet_collection_model import PetId
from .stat_target import PetStatTarget
from .stats import StatNode, Stats, UniqueStat

if TYPE_CHECKING:
	from ..player.player_model import PlayerModel
	from ..player.player_pet_collection_model import PlayerPetModel
	from ..shared_game_config import SharedGameConfig


@dataclass
class PetStatsGameConfig:
	pet_upgrade_library: dict[Rarity, dict]
	pet_balancing_library: dict[PetBalancingType, dict]
	pet_library: dict[PetId, dict]
	tech_tree_library: dict[TechTreeNodeType, dict]
	tech_tree_position_library: dict[TechTreeType, dict]
	ascension_configs_library: dict[AscendableType, dict]
	stat_config_library: dict[tuple[StatType, StatNature], dict]
	secondary_stat_library: dict
	items: dict
	weapons: dict
	pet_base_config: Any
	skill_base_config: Any
	item_balancing_config: Any


_pet_stats_config: PetStatsGameConfig | None = None


@miraesee_extension
def load_pet_stats_config() -> PetStatsGameConfig:
	global _pet_stats_config
	if _pet_stats_config is not None:
		return _pet_stats_config

	import config as cfg
	from ..shared_game_config import (
		ItemBalancingConfig,
		PetBaseConfig,
		SkillBaseConfig,
		build_item_library,
		build_pet_library,
		build_secondary_stat_library,
		build_stat_config_library,
	)

	_pet_stats_config = PetStatsGameConfig(
		pet_upgrade_library={Rarity[k]: v for k, v in cfg.PET_UPGRADE_LIBRARY.items()},
		pet_balancing_library={
			PetBalancingType[k]: v for k, v in cfg.PET_BALANCING_LIBRARY.items()
		},
		pet_library=build_pet_library(cfg.PET_LIBRARY),
		tech_tree_library={
			TechTreeNodeType[name]: data for name, data in cfg.TECH_TREE_LIBRARY.items()
		},
		tech_tree_position_library={
			TechTreeType[k]: v for k, v in cfg.TECH_TREE_POSITION_LIBRARY.items()
		},
		ascension_configs_library={
			AscendableType[name]: data
			for name, data in cfg.ASCENSION_CONFIGS_LIBRARY.items()
		},
		stat_config_library=build_stat_config_library(cfg.STAT_CONFIG_LIBRARY),
		secondary_stat_library=build_secondary_stat_library(cfg.SECONDARY_STAT_LIBRARY),
		items=build_item_library(cfg.ITEM_BALANCING_LIBRARY),
		weapons=build_item_library(cfg.WEAPON_LIBRARY),
		pet_base_config=PetBaseConfig.from_dict(cfg.PET_BASE_CONFIG),
		skill_base_config=SkillBaseConfig.from_dict(cfg.SKILL_BASE_CONFIG),
		item_balancing_config=ItemBalancingConfig.from_dict(cfg.ITEM_BALANCING_CONFIG),
	)
	return _pet_stats_config


def _extract_primary_from_level_info(level_info: dict) -> tuple[float, float]:
	damage = 0.0
	health = 0.0
	for row in level_info.get("PetStats", {}).get("Stats", []):
		stat_type = row["StatNode"]["UniqueStat"]["StatType"]
		value = float(row["Value"])
		if stat_type == "Damage":
			damage = value
		elif stat_type == "Health":
			health = value
	return damage, health


@miraesee_extension
def get_pet_upgrade_base_stats(
	game_config: Any,
	rarity: Rarity,
	level: int,
) -> tuple[float, float]:
	upgrade_cfg = game_config.pet_upgrade_library.get(rarity)
	if upgrade_cfg is None:
		return 0.0, 0.0
	for level_info in upgrade_cfg.get("LevelInfo", []):
		if int(level_info.get("Level", -1)) == level:
			return _extract_primary_from_level_info(level_info)
	return 0.0, 0.0


@miraesee_extension
def get_pet_balancing_multipliers(
	game_config: Any,
	pet_id,
) -> tuple[float, float]:
	pet_cfg = game_config.pet_library.get(pet_id)
	if pet_cfg is None:
		return 1.0, 1.0
	balancing_type = PetBalancingType[pet_cfg["Type"]]
	balancing = game_config.pet_balancing_library.get(balancing_type)
	if balancing is None:
		return 1.0, 1.0
	return float(balancing["DamageMultiplier"]), float(balancing["HealthMultiplier"])


@miraesee_extension
def get_pet_experience_required(
	game_config: Any,
	rarity: Rarity,
	level: int,
) -> int:
	upgrade_cfg = game_config.pet_upgrade_library.get(rarity)
	if upgrade_cfg is None:
		return 0
	for level_info in upgrade_cfg.get("LevelInfo", []):
		if int(level_info.get("Level", -1)) == level:
			return int(level_info.get("Experience", 0))
	return 0


def _filter_pet_tech_tree_stats(full_stats: Stats) -> Stats:
	filtered = Stats()
	for node, value in full_stats.all_stat_contributions.items():
		if not isinstance(node.stat_target, PetStatTarget):
			continue
		if node.unique_stat.stat_type not in (
			StatType.TechTreeDamage,
			StatType.TechTreeHealth,
		):
			continue
		filtered.add_stat_contribution(node, value)
	return filtered


@miraesee_extension
def build_pet_tech_tree_stats(player: PlayerModel) -> Stats:
	return _filter_pet_tech_tree_stats(
		player.player_techtree_model.get_total_stats(player)
	)


def _dependency_multiplier(
	modifier_stats: Stats,
	game_config: Any,
	dep_stat_type: StatType,
) -> float:
	target = PetStatTarget()
	default = float(
		game_config.stat_config_library[(dep_stat_type, StatNature.Multiplier)][
			"DefaultValue"
		]
	)
	node = StatNode(UniqueStat(dep_stat_type, StatNature.Multiplier), target)
	return default + modifier_stats.all_stat_contributions.get(node, 0.0)


@miraesee_extension
def resolve_player_game_config(player: PlayerModel) -> Any:
	return player.game_config


@miraesee_extension
def build_pet_modifier_stats(player: PlayerModel) -> Stats:
	game_config = resolve_player_game_config(player)
	stats = build_pet_tech_tree_stats(player)
	ascension = player.player_pet_collection_model.ascension_model.get_level_stats(
		game_config
	)
	stats.add_stat_contributions(ascension)
	return stats


@miraesee_extension
def resolve_pet_primary_stats(
	player: PlayerModel,
	pet: PlayerPetModel,
) -> tuple[float, float]:
	game_config = resolve_player_game_config(player)
	base_damage, base_health = get_pet_upgrade_base_stats(
		game_config, pet.pet_id.rarity, pet.level
	)
	damage_mult, health_mult = get_pet_balancing_multipliers(game_config, pet.pet_id)
	modifier_stats = build_pet_modifier_stats(player)
	incoming_damage = base_damage * damage_mult
	incoming_health = base_health * health_mult
	damage = incoming_damage * _dependency_multiplier(
		modifier_stats, game_config, StatType.TechTreeDamage
	) * _dependency_multiplier(modifier_stats, game_config, StatType.AscensionDamage)
	health = incoming_health * _dependency_multiplier(
		modifier_stats, game_config, StatType.TechTreeHealth
	) * _dependency_multiplier(modifier_stats, game_config, StatType.AscensionHealth)
	return damage, health


@miraesee_extension
def format_pet_stat_display(value: float) -> str:
	rounded = int(round(value))
	if rounded >= 1_000_000:
		return f"{rounded // 1_000_000}M"
	if rounded >= 1_000:
		return f"{rounded // 1_000}k"
	return str(rounded)
