"""Forge 10x from test_user_dump.txt and resolve item names via Items_Mapping."""
from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.enums import ItemAge
from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

ROOT = Path(__file__).resolve().parents[1]
MAPPING_PATH = ROOT / "config" / "Items_Mapping.json"
DUMP_PATH = ROOT / "test_user_dump.txt"


def item_mapping_key(age: int, item_type: int, idx: int) -> str:
	return f"{age}_{item_type}_{idx}"


def load_item_keys() -> dict[str, str]:
	data = json.loads(MAPPING_PATH.read_text(encoding="utf-8"))
	return {
		key: entry.get("Key", key)
		for key, entry in data.get("items", {}).items()
	}


def main() -> None:
	keys = load_item_keys()
	player = dump_snapshot_to_player_model(
		parse_dump_text(DUMP_PATH.read_text(encoding="utf-8"))
	)
	forge = player.player_forge_model
	print("=== dump state ===")
	print(
		f"forge_level={forge.forge_level} forge_count={forge.forge_count:,} "
		f"seed={forge.forge_seed:#018x}"
	)
	print(
		f"highest_age={forge.highest_age_of_crafted_item} "
		f"(dump) asc={forge.ascension_model.current_level}"
	)

	logic = GameLogic(player)
	print("\n=== forge x10 ===")
	print(f"{'#':>3}  {'mapping':<12} {'Key':<24} {'age':<12} {'type':<10} idx  lv  secondary")
	print("-" * 95)

	for i in range(1, 11):
		result, items = logic.forge(1, commit=True)
		if not items or result.name != "Success":
			print(f"{i:>3}  FAILED: {result.name}")
			break
		it = items[0]
		age_i = int(it.item_id.Age)
		type_i = int(it.item_id.Type)
		idx = it.item_id.Idx
		map_key = item_mapping_key(age_i, type_i, idx)
		name = keys.get(map_key, f"?{map_key}")
		age_name = ItemAge(age_i).name
		sec = []
		if it.secondary_stats:
			sec = [s.name for s in it.secondary_stats.interpolated_stat_values]
		print(
			f"{i:>3}  {map_key:<12} {name:<24} {age_name:<12} "
			f"{it.item_id.Type.name:<10} {idx:<3} {it.level:<3} {sec}"
		)

	print(
		f"\nseed_after={forge.forge_seed:#018x} "
		f"forge_count_after={forge.forge_count:,}"
	)


if __name__ == "__main__":
	main()
