from __future__ import annotations

import json
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = _PROJECT_ROOT

CONFIG_DIR = PROJECT_ROOT / "config"
CORE_DIR = PROJECT_ROOT / "core"
UI_DIR = PROJECT_ROOT / "ui"
UTILS_DIR = PROJECT_ROOT / "utils"
ASSETS_DIR = PROJECT_ROOT / "assets"

GAME_CONFIGS_DIR = ASSETS_DIR / "game_configs"
LOCALIZATIONS_DIR = ASSETS_DIR / "localizations"
SPRITES_DIR = ASSETS_DIR / "sprites"
UI_SPRITES_DIR = SPRITES_DIR / "UI"
UI_META_FILE = UI_SPRITES_DIR / "UI_meta.json"
_FONTS_CANDIDATE = ASSETS_DIR / "Fonts"
FONTS_DIR = _FONTS_CANDIDATE if _FONTS_CANDIDATE.is_dir() else ASSETS_DIR / "fonts"

GAME_LOGIC_DIR = CORE_DIR / "game_logic"


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
SKINS_MAPPING = load_json(CONFIG_DIR / "Skins_Mapping.json")
SPRITE_SHEETS = load_json(CONFIG_DIR / "SpriteSheets.json")


IN_APP_PRODUCTS = load_json(GAME_CONFIGS_DIR / "InAppProducts.json")
BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "BaseConfig.json")
FORGE_CONFIG = load_json(GAME_CONFIGS_DIR / "ForgeConfig.json")
ITEM_BALANCING_CONFIG = load_json(GAME_CONFIGS_DIR / "ItemBalancingConfig.json")
SECONDARY_STAT_LIBRARY = load_json(GAME_CONFIGS_DIR / "SecondaryStatLibrary.json")
SECONDARY_STAT_ITEM_UNLOCK_LIBRARY = load_json(GAME_CONFIGS_DIR / "SecondaryStatItemUnlockLibrary.json")
ITEM_BALANCING_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemBalancingLibrary.json")
PROJECTILES_LIBRARY = load_json(GAME_CONFIGS_DIR / "ProjectilesLibrary.json")
WEAPON_LIBRARY = load_json(GAME_CONFIGS_DIR / "WeaponLibrary.json")
ITEM_AGE_DROP_CHANCES_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemAgeDropChancesLibrary.json")
ITEM_LEVEL_BRACKETS_LIBRARY = load_json(GAME_CONFIGS_DIR / "ItemLevelBracketsLibrary.json")
FORGE_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "ForgeUpgradeLibrary.json")
MAIN_BATTLE_CONFIG = load_json(GAME_CONFIGS_DIR / "MainBattleConfig.json")
MAIN_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "MainBattleLibrary.json")
ENEMY_LIBRARY = load_json(GAME_CONFIGS_DIR / "EnemyLibrary.json")
ENEMY_AGE_SCALING_LIBRARY = load_json(GAME_CONFIGS_DIR / "EnemyAgeScalingLibrary.json")
SKILL_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "SkillBaseConfig.json")
SKILL_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillLibrary.json")
SKILL_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillUpgradeLibrary.json")
SKILL_PASSIVE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillPassiveLibrary.json")
STAT_CONFIG_LIBRARY = load_json(GAME_CONFIGS_DIR / "StatConfigLibrary.json")
TECH_TREE_LIBRARY = load_json(GAME_CONFIGS_DIR / "TechTreeLibrary.json")
TECH_TREE_POSITION_LIBRARY = load_json(GAME_CONFIGS_DIR / "TechTreePositionLibrary.json")
TECH_TREE_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "TechTreeUpgradeLibrary.json")
PET_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetLibrary.json")
SECONDARY_STAT_PET_UNLOCK_LIBRARY = load_json(GAME_CONFIGS_DIR / "SecondaryStatPetUnlockLibrary.json")
PET_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetUpgradeLibrary.json")
PET_BALANCING_LIBRARY = load_json(GAME_CONFIGS_DIR / "PetBalancingLibrary.json")
EGG_LIBRARY = load_json(GAME_CONFIGS_DIR / "EggLibrary.json")
PET_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "PetBaseConfig.json")
DUNGEON_REWARD_LIBRARY = load_json(GAME_CONFIGS_DIR / "DungeonRewardLibrary.json")
SKILL_DUNGEON_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkillDungeonBattleLibrary.json")
POTION_DUNGEON_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "PotionDungeonBattleLibrary.json")
EGG_DUNGEON_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "EggDungeonBattleLibrary.json")
HAMMER_THIEF_DUNGEON_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "HammerThiefDungeonBattleLibrary.json")
DUNGEON_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "DungeonBaseConfig.json")
SHOP_RESOURCES_LIBRARY = load_json(GAME_CONFIGS_DIR / "ShopResourcesLibrary.json")
DAILY_DEAL_LIBRARY = load_json(GAME_CONFIGS_DIR / "DailyDealLibrary.json")
IDLE_CONFIG = load_json(GAME_CONFIGS_DIR / "IdleConfig.json")
EGG_SUMMON_CONFIG = load_json(GAME_CONFIGS_DIR / "EggSummonConfig.json")
MOUNT_SUMMON_CONFIG = load_json(GAME_CONFIGS_DIR / "MountSummonConfig.json")
SKILL_SUMMON_CONFIG = load_json(GAME_CONFIGS_DIR / "SkillSummonConfig.json")
MOUNT_LIBRARY = load_json(GAME_CONFIGS_DIR / "MountLibrary.json")
MOUNT_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "MountUpgradeLibrary.json")
SKINS_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkinsLibrary.json")
SKIN_UPGRADE_LIBRARY = load_json(GAME_CONFIGS_DIR / "SkinUpgradeLibrary.json")
SETS_LIBRARY = load_json(GAME_CONFIGS_DIR / "SetsLibrary.json")
PLAYER_SEGMENTS= load_json(GAME_CONFIGS_DIR / "PlayerSegments.json")
UNLOCK_CONDITIONS = load_json(GAME_CONFIGS_DIR / "UnlockConditions.json")
PROFILE_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "ProfileBaseConfig.json")
PVP_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "PvpBaseConfig.json")
ARENA_REWARD_LIBRARY = load_json(GAME_CONFIGS_DIR / "ArenaRewardLibrary.json")
ARENA_LEAGUE_LIBRARY = load_json(GAME_CONFIGS_DIR / "ArenaLeagueLibrary.json")
GUILD_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "GuildBaseConfig.json")
GUILD_WAR_CONFIG = load_json(GAME_CONFIGS_DIR / "GuildWarConfig.json")
GUILD_TIER_CONFIG = load_json(GAME_CONFIGS_DIR / "GuildTierConfig.json")
GUILD_EMBLEM_COLORS = load_json(GAME_CONFIGS_DIR / "GuildEmblemColors.json")
MAIN_GAME_PROGRESS_PASS_LIBRARY = load_json(GAME_CONFIGS_DIR / "MainGameProgressPassLibrary.json")
GUILD_WAR_PROGRESS_PASS_LIBRARY = load_json(GAME_CONFIGS_DIR / "GuildWarProgressPassLibrary.json")
GUILD_WAR_DAY_CONFIG_LIBRARY = load_json(GAME_CONFIGS_DIR / "GuildWarDayConfigLibrary.json")
WORLD_INDEX_CONFIG_LIBRARY = load_json(GAME_CONFIGS_DIR / "WorldIndexConfigLibrary.json")
ASCENSION_CONFIGS_LIBRARY = load_json(GAME_CONFIGS_DIR / "AscensionConfigsLibrary.json")
MISSION_LEVEL_LIBRARY = load_json(GAME_CONFIGS_DIR / "MissionLevelLibrary.json")
MISSION_BATTLE_LIBRARY = load_json(GAME_CONFIGS_DIR / "MissionBattleLibrary.json")
MISSION_REWARD_LIBRARY = load_json(GAME_CONFIGS_DIR / "MissionRewardLibrary.json")
MISSION_RALLY_TIME_LIBRARY = load_json(GAME_CONFIGS_DIR / "MissionRallyTimeLibrary.json")
MISSION_ALL_MEMBER_REWARD_LIBRARY = load_json(GAME_CONFIGS_DIR / "MissionAllMemberRewardLibrary.json")
MISSION_BASE_CONFIG = load_json(GAME_CONFIGS_DIR / "MissionBaseConfig.json")
LEGACY_DUNGEONS_MIGRATION = load_json(GAME_CONFIGS_DIR / "LegacyDungeonsMigration.json")
