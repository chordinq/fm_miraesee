"""Forge 5x from dump and format like in-game verification table."""
from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.enums import ItemAge, SecondaryStatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.stats.secondary_stat_helper import SecondaryStatHelper
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "config" / "Items_Mapping.json"
DUMP_PATH = ROOT / "test_user_dump.txt"

STAT_LABELS = {
	SecondaryStatType.LifeSteal: "lifesteal",
	SecondaryStatType.MeleeDamageMulti: "MeleeDmg",
	SecondaryStatType.RangedDamageMulti: "Ranged Damage",
	SecondaryStatType.DamageMulti: "Damage",
	SecondaryStatType.SkillCooldownMulti: "Skillcooldown",
	SecondaryStatType.CriticalMulti: "Critical",
	SecondaryStatType.BlockChance: "Block",
	SecondaryStatType.HealthMulti: "Health",
	SecondaryStatType.SkillDamageMulti: "SkillDmg",
}


def load_item_keys() -> dict[str, str]:
	data = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
	return {key: entry.get("Key", key) for key, entry in data.get("items", {}).items()}


def fmt_stat(stat_type: SecondaryStatType, value: float) -> str:
	label = STAT_LABELS.get(stat_type, stat_type.name)
	# UI shows percent for most multipliers; cooldown often shown negative when < 1
	if stat_type == SecondaryStatType.SkillCooldownMulti:
		pct = (value - 1.0) * 100.0
		return f"{label} {pct:+.2f}%"
	pct = value * 100.0
	return f"{label} +{pct:.2f}%"


def main() -> None:
	keys = load_item_keys()
	player = dump_snapshot_to_player_model(
		parse_dump_text(DUMP_PATH.read_text(encoding="utf-8"))
	)
	forge = player.player_forge_model
	gc = player.game_config
	print("=== dump ===")
	print(
		f"level={forge.forge_level} count={forge.forge_count:,} "
		f"seed={forge.forge_seed:#x} highest_age={forge.highest_age_of_crafted_item}"
	)

	logic = GameLogic(player)
	print("\n#  lv  Age       type      Name              Stat1                  Stat2")
	print("-" * 85)

	for i in range(1, 6):
		result, items = logic.forge(1, commit=True)
		if not items or result.name != "Success":
			print(f"{i}  FAILED {result.name}")
			break
		it = items[0]
		age_i = int(it.item_id.Age)
		type_i = int(it.item_id.Type)
		map_key = f"{age_i}_{type_i}_{it.item_id.Idx}"
		name = keys.get(map_key, map_key)
		age_short = ItemAge(age_i).name
		if age_short == "Multiverse":
			age_short = "multi"

		stat_parts: list[str] = []
		if it.secondary_stats:
			for st in it.secondary_stats.interpolated_stat_values:
				_, resolved = it.secondary_stats.try_get_stat_value(st, gc)
				stat_parts.append(fmt_stat(st, resolved))

		s1 = stat_parts[0] if len(stat_parts) > 0 else "-"
		s2 = stat_parts[1] if len(stat_parts) > 1 else "-"
		print(
			f"{i:<2} {it.level:<3} {age_short:<9} {it.item_id.Type.name:<9} "
			f"{name:<17} {s1:<22} {s2}"
		)

	print(f"\nseed_after={forge.forge_seed:#x}")


if __name__ == "__main__":
	main()
