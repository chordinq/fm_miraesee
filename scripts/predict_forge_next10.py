"""Predict forge results from dump (supports skip + level column)."""
from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.actions.forge.forge_action import (
	_create_forge_item,
	_get_possible_items,
)
from core.game_logic.enums import ItemAge, ItemType, SecondaryStatType, StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.item_age_drop import roll_age
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import ForgeStatTarget
from core.random_pcg import RandomPCG
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "test_user_dump.txt"
KEYS = {
	k: v["Key"]
	for k, v in json.loads((ROOT / "config" / "Items_Mapping.json").read_text())["items"].items()
}

TYPE_KOR = {
	ItemType.Helmet: "투구",
	ItemType.Armour: "갑옷",
	ItemType.Gloves: "장갑",
	ItemType.Necklace: "목걸이",
	ItemType.Ring: "반지",
	ItemType.Shoes: "신발",
	ItemType.Belt: "벨트",
}
AGE_KOR = {
	ItemAge.Multiverse: "다중우주",
	ItemAge.Quantum: "양자",
	ItemAge.Underworld: "지하세계",
	ItemAge.Divine: "신성",
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
	SecondaryStatType.HealthRegen: "HealthRegen",
}

KNOWN_FIRST10 = [
	("NeutronFingerprints", False),
	("BlackSpear", True),
	("BlackStaff", True),
	("VoidNecklace", False),
	("NeutrinoBelt", False),
	("BlackBelt", False),
	("Casquette", True),  # in-game marked free; sim says not free at 10%
	("ConnectionRing", False),
	("Skullbinder", False),
	("AntigravityBoots", False),
]


def weapon_type_label(item, gc) -> str:
	if item.item_id.Type != ItemType.Weapon:
		return TYPE_KOR.get(item.item_id.Type, item.item_id.Type.name)
	info = gc.weapons.get(item.item_id)
	if info and info.get("IsRanged"):
		return "원거리"
	return "근거리"


def stat_pct(item, gc, stat_type: SecondaryStatType) -> float:
	_, value = item.secondary_stats.try_get_stat_value(stat_type, gc)
	return value * 100.0


def fmt_stats(item, gc) -> tuple[str, str]:
	if not item.secondary_stats:
		return "-", "-"
	parts: list[str] = []
	for st in item.secondary_stats.interpolated_stat_values:
		label = STAT_LABEL.get(st, st.name)
		parts.append(f"{label} (+{stat_pct(item, gc, st):.2f}%)")
	s1 = parts[0] if parts else "-"
	s2 = parts[1] if len(parts) > 1 else "-"
	return s1, s2


def detect_free(player, seed: int) -> bool:
	rng = RandomPCG.create_from_seed(seed)
	age = roll_age(player, rng)
	_create_forge_item(player, _get_possible_items(player.game_config, age), rng, age)
	return StatHelper.roll_stat(player, StatType.FreebieChance, ForgeStatTarget(), rng)


def forge_rows(player, logic, gc, count: int) -> list[dict]:
	rows: list[dict] = []
	for _ in range(count):
		seed = player.player_forge_model.forge_seed
		free = detect_free(player, seed)
		_, items = logic.forge(1, commit=True)
		item = items[0]
		map_key = f"{int(item.item_id.Age)}_{int(item.item_id.Type)}_{item.item_id.Idx}"
		s1, s2 = fmt_stats(item, gc)
		rows.append(
			{
				"age": AGE_KOR.get(item.item_id.Age, item.item_id.Age.name),
				"type": weapon_type_label(item, gc),
				"name": KEYS.get(map_key, map_key),
				"level": item.level,
				"s1": s1,
				"s2": s2,
				"free": free,
				"seed": seed,
			}
		)
	return rows


def print_prediction_block(
	title: str,
	rows: list[dict],
	start_n: int,
	start_seed: int,
) -> None:
	free_n = sum(1 for r in rows if r["free"])
	ages: dict[str, int] = {}
	for r in rows:
		ages[r["age"]] = ages.get(r["age"], 0) + 1
	age_summary = " | ".join(f"{a}: {n}" for a, n in ages.items())
	end_seed = start_seed + len(rows) - 1
	print(f"=== {title} (seed {start_seed:#x} ~ {end_seed:#x}) ===")
	print(f"예상 무료: {free_n}회 | 티어: {age_summary}")
	print()
	print(f"{'#':>3}  {'티어':^6}  {'타입':^6}  {'Lv':>3}  {'아이템':<20}  {'스탯1':<36}  {'스탯2':<36}  무료")
	print("-" * 120)
	for i, row in enumerate(rows, start_n):
		free_mark = "🍀" if row["free"] else "  "
		print(
			f"{i:>3}  {row['age']:^6}  {row['type']:^6}  {row['level']:>3}  "
			f"{row['name']:<20}  {row['s1']:<36}  {row['s2']:<36}  {free_mark}"
		)
	print()


def main() -> None:
	import sys

	skip = 20
	predict = 10
	if len(sys.argv) >= 2:
		skip = int(sys.argv[1])
	if len(sys.argv) >= 3:
		predict = int(sys.argv[2])

	player = dump_snapshot_to_player_model(
		parse_dump_text(DUMP.read_text(encoding="utf-8"))
	)
	gc = player.game_config
	forge = player.player_forge_model
	logic = GameLogic(player)

	start_seed = forge.forge_seed
	start_count = forge.forge_count

	if skip > 0:
		forge_rows(player, logic, gc, skip)

	pred_seed = forge.forge_seed
	rows = forge_rows(player, logic, gc, predict)

	print("=== 현재 상태 ===")
	print(
		f"dump seed={start_seed:#x}  count={start_count:,}  "
		f"→ skip {skip}회 후 seed={pred_seed:#x}"
	)
	print()
	print_prediction_block(
		f"{skip + 1}~{skip + predict}회 예상",
		rows,
		skip + 1,
		pred_seed,
	)
	print(
		f"{skip + predict}회 후: seed={forge.forge_seed:#x}  "
		f"count={forge.forge_count:,}"
	)


if __name__ == "__main__":
	main()
