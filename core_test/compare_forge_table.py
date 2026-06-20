"""Compare simulator 5x forge vs user in-game table."""
from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.enums import ItemAge, SecondaryStatType
from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

ROOT = Path(__file__).resolve().parents[1]
DUMP = ROOT / "test_user_dump.txt"
KEYS = {
	k: v["Key"]
	for k, v in json.loads((ROOT / "config" / "Items_Mapping.json").read_text())["items"].items()
}

EXPECTED = [
	(105, 7, 0, 4, "SubMask", "LifeSteal", 0.167, "MeleeDamageMulti", 0.0396),
	(108, 6, 2, 0, "Impulse", "DamageMulti", 0.0531, None, None),
	(103, 6, 0, 1, "IronHolo", "LifeSteal", 0.196, None, None),
	(108, 6, 1, 0, "HoloArmor", "SkillCooldownMulti", 0.9598, None, None),  # -4.02% display
	(105, 6, 6, 0, "EtherealSocks", "RangedDamageMulti", 0.105, None, None),
]

STAT = {
	"LifeSteal": SecondaryStatType.LifeSteal,
	"MeleeDamageMulti": SecondaryStatType.MeleeDamageMulti,
	"DamageMulti": SecondaryStatType.DamageMulti,
	"SkillCooldownMulti": SecondaryStatType.SkillCooldownMulti,
	"RangedDamageMulti": SecondaryStatType.RangedDamageMulti,
}


def fmt_row(i: int, it, gc) -> str:
	age = int(it.item_id.Age)
	t = int(it.item_id.Type)
	key = f"{age}_{t}_{it.item_id.Idx}"
	name = KEYS.get(key, key)
	parts = []
	if it.secondary_stats:
		for st, _t in it.secondary_stats.interpolated_stat_values.items():
			_, v = it.secondary_stats.try_get_stat_value(st, gc)
			parts.append(f"{st.name}={v:.4f}")
	return f"{i} lv={it.level} {ItemAge(age).name}/{it.item_id.Type.name} {name} {' '.join(parts)}"


def run_forge_5(seed: int | None = None) -> list:
	player = dump_snapshot_to_player_model(parse_dump_text(DUMP.read_text(encoding="utf-8")))
	if seed is not None:
		player.player_forge_model.forge_seed = seed
	logic = GameLogic(player)
	items = []
	for _ in range(5):
		_, batch = logic.forge(1)
		items.append(batch[0])
	return player, items


def main() -> None:
	dump_seed = parse_dump_text(DUMP.read_text(encoding="utf-8")).forge_meta.forge_seed
	player, items = run_forge_5()
	f = player.player_forge_model
	gc = player.game_config
	print(f"dump seed={dump_seed:#x} -> after 5 forges={f.forge_seed:#x}")
	print("\n=== SIM ===")
	for i, it in enumerate(items, 1):
		print(fmt_row(i, it, gc))

	print("\n=== EXPECTED (in-game) ===")
	for i, row in enumerate(EXPECTED, 1):
		lv, age, typ, idx, name, s1n, s1v, s2n, s2v = row
		s2 = f" {s2n}={s2v}" if s2n else ""
		print(f"{i} lv={lv} {ItemAge(age).name}/{ItemAge(age)} {name} {s1n}={s1v}{s2}")

	print("\n=== MATCH ===")
	for i, (it, exp) in enumerate(zip(items, EXPECTED), 1):
		lv, age, typ, idx, name, s1n, s1v, s2n, s2v = exp
		key = KEYS.get(f"{int(it.item_id.Age)}_{int(it.item_id.Type)}_{it.item_id.Idx}")
		ok_name = key == name
		ok_lv = it.level == lv
		ok_stats = True
		if it.secondary_stats and s1n:
			st = STAT[s1n]
			_, v = it.secondary_stats.try_get_stat_value(st, gc)
			ok_stats = abs(v - s1v) < 0.02
		print(f"{i} name={'OK' if ok_name else 'MISS'}({key} vs {name}) lv={'OK' if ok_lv else f'{it.level} vs {lv}'} stats={'OK' if ok_stats else 'MISS'}")

	# seed scan around dump seed
	base = dump_seed
	print(f"\n=== seed scan (first item SubMask) base={base:#x} ===")
	for off in range(-20, 21):
		p, its = run_forge_5(base + off)
		k = f"{int(its[0].item_id.Age)}_{int(its[0].item_id.Type)}_{its[0].item_id.Idx}"
		if KEYS.get(k) == "SubMask":
			print(f"  off={off:+d} seed={base+off:#x} -> {[KEYS.get(f'{int(x.item_id.Age)}_{int(x.item_id.Type)}_{x.item_id.Idx}') for x in its]}")


if __name__ == "__main__":
	main()
