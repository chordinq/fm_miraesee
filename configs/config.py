# configs/config.py
import json
import os
from .enums import AscendableType

def load_json(filepath):
	with open(filepath, 'r', encoding='utf-8') as f:
		return json.load(f)

ENG_KOR_MAPPING = load_json('configs/EngKorMapping.json')
ITEM_MAPPING = load_json('configs/ItemMapping.json')
MOUNT_MAPPING = load_json('configs/MountMapping.json')
PET_MAPPING = load_json('configs/PetMapping.json')
SKILL_MAPPING = load_json('configs/SkillMapping.json')

def load_stat_ranges():
	data = load_json('configs/library/SecondaryStatLibrary.json')
	return {
		key: {"lower": val["LowerRange"], "upper": val["UpperRange"]}
		for key, val in data.items()
	}

STAT_RANGES = load_stat_ranges()

SUMMON_CONFIGS = {
	AscendableType.Skills: load_json('configs/library/SkillSummonConfig.json'),
	AscendableType.Pets: load_json('configs/library/EggSummonConfig.json'),
	AscendableType.Mounts: load_json('configs/library/MountSummonConfig.json')
}