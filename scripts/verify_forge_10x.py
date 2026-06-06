"""Compare 10x forge (round-robin on) vs in-game table from old forge.py verification."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from core.game_logic.enums import ItemAge, ItemType, SecondaryStatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import ForgeStatTarget
from core.game_logic.enums import StatType
from core.random_pcg import RandomPCG
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "test_user_dump.txt"
KEYS = {
	k: v["Key"]
	for k, v in json.loads((ROOT / "config" / "Items_Mapping.json").read_text())["items"].items()
}

STAT_LABEL = {
	SecondaryStatType.CriticalMulti: "Critical Damage",
	SecondaryStatType.DoubleDamageChance: "Double Chance",
	SecondaryStatType.MeleeDamageMulti: "Melee Damage",
	SecondaryStatType.DamageMulti: "Damage",
	SecondaryStatType.SkillCooldownMulti: "Skill Cooldown",
	SecondaryStatType.SkillDamageMulti: "Skill Damage",
	SecondaryStatType.BlockChance: "Block Chance",
	SecondaryStatType.CriticalChance: "Critical Chance",
	SecondaryStatType.LifeSteal: "Life Steal",
	SecondaryStatType.RangedDamageMulti: "Ranged Damage",
	SecondaryStatType.HealthMulti: "Health",
	SecondaryStatType.AttackSpeed: "Attack Speed",
}


@dataclass
class ExpectedRow:
	age: int
	item_type: int
	weapon_melee: bool | None  # None = not weapon
	key: str
	stats: list[tuple[str, float]]  # label, pct value
	free: bool


EXPECTED: list[ExpectedRow] = [
	ExpectedRow(7, 2, None, "NeutronFingerprints", [("Critical Damage", 47.89), ("Double Chance", 5.27)], False),
	ExpectedRow(7, 5, True, "BlackSpear", [("Melee Damage", 11.55), ("Damage", 14.72)], True),
	ExpectedRow(7, 5, False, "BlackStaff", [("Skill Cooldown", 3.32), ("Skill Damage", 3.54)], True),
	ExpectedRow(7, 3, None, "VoidNecklace", [("Block Chance", 2.61), ("Critical Chance", 8.85)], False),
	ExpectedRow(7, 7, None, "NeutrinoBelt", [("Critical Damage", 62.07), ("Skill Cooldown", 5.25)], False),
	ExpectedRow(7, 7, None, "BlackBelt", [("Block Chance", 4.18), ("Critical Damage", 29.04)], False),
	ExpectedRow(6, 0, None, "Casquette", [("Life Steal", 18.84)], True),
	ExpectedRow(6, 4, None, "ConnectionRing", [("Attack Speed", 3.88)], False),
	ExpectedRow(8, 4, None, "Skullbinder", [("Ranged Damage", 2.42), ("Skill Damage", 17.18)], False),
	ExpectedRow(7, 6, None, "AntigravityBoots", [("Health", 13.52), ("Skill Damage", 21.80)], False),
]


def stat_pct(item, gc, stat_type: SecondaryStatType) -> float:
	_, v = item.secondary_stats.try_get_stat_value(stat_type, gc)
	return v * 100.0


def detect_freebie_after_forge(player, seed: int) -> bool:
	"""Legacy forge.py / in-game: freebie roll after item RNG on this seed."""
	from core.game_logic.actions.forge.forge_action import (
		_create_forge_item,
		_get_possible_items,
	)
	from core.game_logic.item_age_drop import roll_age

	rng = RandomPCG.create_from_seed(seed)
	age = roll_age(player, rng)
	possible = _get_possible_items(player.game_config, age)
	item = _create_forge_item(player, possible, rng, age)
	if item is None:
		return False
	return StatHelper.roll_stat(player, StatType.FreebieChance, ForgeStatTarget(), rng)


def weapon_kind(item, gc) -> str | None:
	if item.item_id.Type != ItemType.Weapon:
		return None
	info = gc.weapons.get(item.item_id)
	if info and info.get("IsRanged"):
		return "ranged"
	return "melee"


def main() -> None:
	player = dump_snapshot_to_player_model(parse_dump_text(DUMP.read_text(encoding="utf-8")))
	forge = player.player_forge_model
	gc = player.game_config
	dump = parse_dump_text(DUMP.read_text(encoding="utf-8")).forge_meta
	print("=== dump ===")
	print(
		f"seed={dump.forge_seed:#x} count={dump.forge_count:,} "
		f"highest_age={dump.highest_age_of_crafted_item}"
	)

	logic = GameLogic(player)
	free_count = 0
	print("\n#  match  age type  Key                 stats (sim)                    free")
	print("-" * 95)

	for i, exp in enumerate(EXPECTED, 1):
		seed_before = forge.forge_seed
		free = detect_freebie_after_forge(player, seed_before)
		result, items = logic.forge(1, commit=True)
		it = items[0]
		if free:
			free_count += 1

		map_key = f"{int(it.item_id.Age)}_{int(it.item_id.Type)}_{it.item_id.Idx}"
		name = KEYS.get(map_key, map_key)

		ok_age = int(it.item_id.Age) == exp.age
		ok_type = int(it.item_id.Type) == exp.item_type
		ok_name = name == exp.key
		ok_free = free == exp.free

		sim_stats: list[tuple[str, float]] = []
		if it.secondary_stats:
			for st in it.secondary_stats.interpolated_stat_values:
				label = STAT_LABEL.get(st, st.name)
				sim_stats.append((label, stat_pct(it, gc, st)))

		ok_stats = True
		for j, (label, pct) in enumerate(exp.stats):
			if j >= len(sim_stats):
				ok_stats = False
				break
			sl, sp = sim_stats[j]
			if sl != label or abs(sp - pct) > 0.15:
				ok_stats = False

		if exp.weapon_melee is not None:
			wk = weapon_kind(it, gc)
			if exp.weapon_melee and wk != "melee":
				ok_name = False
			if not exp.weapon_melee and wk != "ranged":
				ok_name = False

		all_ok = ok_age and ok_type and ok_name and ok_stats and ok_free
		stat_str = " | ".join(f"{l} {p:.2f}%" for l, p in sim_stats) if sim_stats else "-"
		print(
			f"{i:>2} {'OK' if all_ok else 'MISS':4} "
			f"{ItemAge(int(it.item_id.Age)).name[:3]} T{int(it.item_id.Type)} "
			f"{name:<18} {stat_str[:45]:<45} free={free}"
		)
		if not all_ok:
			exp_s = " | ".join(f"{l} {p:.2f}%" for l, p in exp.stats)
			print(f"     expect: {exp.key} {exp_s} free={exp.free}")

	print(f"\nfree_count sim={free_count} expected=3 seed_after={forge.forge_seed:#x}")


if __name__ == "__main__":
	main()
