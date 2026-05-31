# config/__init__.py — paths + game JSON + mapping loaders (single import path)
from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.summon_config import SummonConfig
from .paths import (
	ASSETS_DIR,
	CONFIG_DIR,
	GAME_CONFIGS_DIR,
	LOCALIZATIONS_DIR,
	PROJECT_ROOT,
	SPRITES_DIR,
)


def load_json(file_path: Path) -> dict:
	with open(file_path, "r", encoding="utf-8") as f:
		return json.load(f)


GENERAL_MAPPING = load_json(CONFIG_DIR / "General_Mapping.json")
ITEMS_MAPPING = load_json(CONFIG_DIR / "Items_Mapping.json")
MOUNTS_MAPPING = load_json(CONFIG_DIR / "Mounts_Mapping.json")
PETS_MAPPING = load_json(CONFIG_DIR / "Pets_Mapping.json")
SKILLS_MAPPING = load_json(CONFIG_DIR / "Skills_Mapping.json")
STATS_MAPPING = load_json(CONFIG_DIR / "Stats_Mapping.json")
TECHTREE_MAPPING = load_json(CONFIG_DIR / "TechTree_Mapping.json")

FORGE_CONFIG = load_json(GAME_CONFIGS_DIR / "ForgeConfig.json")

ITEM_AGE_DROP_CHANCES_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemAgeDropChancesLibrary.json")
ITEM_LEVEL_BRACKETS_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemLevelBracketsLibrary.json")
ITEM_BALANCING_CONFIG = load_json(GAME_CONFIGS_DIR / "ItemBalancingConfig.json")
ITEM_BALANCING_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemBalancingLibrary.json")
WEAPON_LIBRARY = load_json(GAME_CONFIGS_DIR / "WeaponLibrary.json")

SKILL_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillLibrary.json")
SKILL_SUMMON_CONFIG = SummonConfig(load_json(GAME_CONFIGS_DIR / "SkillSummonConfig.json"))
SKILL_PASSIVE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillPassiveLibrary.json")
SKILL_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillUpgradeLibrary.json")

EGG_LIBRARY = load_json(GAME_CONFIGS_DIR / "EggLibrary.json")
PET_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetLibrary.json")
EGG_SUMMON_CONFIG = SummonConfig(load_json(GAME_CONFIGS_DIR / "EggSummonConfig.json"))
PET_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetUpgradeLibrary.json")
PET_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "PetBaseConfig.json")
PET_BALANCING_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetBalancingLibrary.json")

MOUNT_LIBRARY = load_json(GAME_CONFIGS_DIR / "MountLibrary.json")
MOUNT_SUMMON_CONFIG = SummonConfig(load_json(GAME_CONFIGS_DIR / "MountSummonConfig.json"))
MOUNT_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "MountUpgradeLibrary.json")

TECH_TREE_LIBRARY = load_json(GAME_CONFIGS_DIR / "TechTreeLibrary.json")
TECH_TREE_POSITION_LIBRARY = load_json(GAME_CONFIGS_DIR / "TechTreePositionLibrary.json")

SECONDARY_STAT_LIBRARY = load_json(GAME_CONFIGS_DIR / "SecondaryStatLibrary.json")
SECONDARY_STAT_PET_UNLOCK = load_json(GAME_CONFIGS_DIR / "SecondaryStatPetUnlockLibrary.json")
SECONDARY_STAT_ITEM_UNLOCK = load_json(GAME_CONFIGS_DIR / "SecondaryStatItemUnlockLibrary.json")





STAT_RANGES: dict[str, dict[str, float]] = {
    name: {
        "lower": float(data["LowerRange"]),
        "upper": float(data["UpperRange"]),
    }
    for name, data in SECONDARY_STAT_LIBRARY.items()
}

STAT_DISPLAY_NAMES: dict[str, str] = {
    entry["Key"]: entry["Key"]
    for entry in STATS_MAPPING.get("SecondaryStatType", {}).values()
}
