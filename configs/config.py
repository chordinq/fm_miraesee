# configs/config.py
import json
from core.enums import AscendableType
from core.game_logic.summon_config import SummonConfig


def load_json(filepath: str) -> dict:
	with open(filepath, "r", encoding="utf-8") as f:
		return json.load(f)


def _load_json_optional(filepath: str) -> dict:
	try:
		return load_json(filepath)
	except FileNotFoundError:
		return {}


ENG_KOR_MAPPING  = _load_json_optional("configs/EngKorMapping.json")
UI_KOR_MAPPING   = _load_json_optional("configs/UiKorMapping.json")
ITEM_MAPPING     = load_json("configs/ItemMapping.json")
AUTO_ITEM_MAPPING = load_json("configs/AutoItemMapping.json")
MOUNT_MAPPING    = load_json("configs/MountMapping.json")
PET_MAPPING      = load_json("configs/PetMapping.json")
SKILL_MAPPING    = load_json("configs/SkillMapping.json")
MANUAL_SPRITE_MAPPING = load_json("configs/ManualSpriteMapping.json")


def _stat_ranges() -> dict:
	data = load_json("configs/parsed_configs/SecondaryStatLibrary.json")
	return {k: {"lower": v["LowerRange"], "upper": v["UpperRange"]} for k, v in data.items()}


STAT_RANGES = _stat_ranges()

SKILL_LIBRARY           = load_json("configs/parsed_configs/SkillLibrary.json")
SKILL_UPGRADE_LIBRARY   = load_json("configs/parsed_configs/SkillUpgradeLibrary.json")
PET_LIBRARY             = load_json("configs/parsed_configs/PetLibrary.json")
MOUNT_LIBRARY           = load_json("configs/parsed_configs/MountLibrary.json")
ITEM_BALANCING_LIBRARY  = load_json("configs/parsed_configs/ItemBalancingLibrary.json")
ITEM_AGE_DROP_CHANCES   = load_json("configs/parsed_configs/ItemAgeDropChancesLibrary.json")
SECONDARY_STAT_UNLOCK     = load_json("configs/parsed_configs/SecondaryStatItemUnlockLibrary.json")
SECONDARY_STAT_PET_UNLOCK = load_json("configs/parsed_configs/SecondaryStatPetUnlockLibrary.json")
ITEM_LEVEL_BRACKETS     = load_json("configs/parsed_configs/ItemLevelBracketsLibrary.json")
FORGE_CONFIG            = load_json("configs/parsed_configs/ForgeConfig.json")
WEAPON_LIBRARY          = load_json("configs/parsed_configs/WeaponLibrary.json")
TECH_TREE_POSITION_LIBRARY = load_json("configs/parsed_configs/TechTreePositionLibrary.json")

SKILL_SUMMON_CONFIG  = SummonConfig(load_json("configs/parsed_configs/SkillSummonConfig.json"))
EGG_SUMMON_CONFIG    = SummonConfig(load_json("configs/parsed_configs/EggSummonConfig.json"))
MOUNT_SUMMON_CONFIG  = SummonConfig(load_json("configs/parsed_configs/MountSummonConfig.json"))

SUMMON_CONFIGS = {
	AscendableType.Skills: SKILL_SUMMON_CONFIG,
	AscendableType.Pets:   EGG_SUMMON_CONFIG,
	AscendableType.Mounts: MOUNT_SUMMON_CONFIG,
}
