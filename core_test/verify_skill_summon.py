"""Verify SkillSummonAction against dump summon meta state transitions."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType
from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def _load_dump_player() -> GameLogic:
	dump_path = Path(__file__).resolve().parent / "test_user_dump.txt"
	text = dump_path.read_text(encoding="utf-8")
	player = dump_snapshot_to_player_model(parse_dump_text(text))
	return GameLogic(player)


def main() -> None:
	logic = _load_dump_player()
	player = logic.player
	collection = player.player_skill_collection_model
	summon = collection.summon_model
	currency = player.player_currency_model

	print("=== Before summon ===")
	print(f"  seed={summon.seed:#018x}  level={summon.level}  count={summon.count}")
	tickets = currency.get(CurrencyType.SkillSummonTickets)
	summon_config = player.game_config.skill_summon_config
	base_cost = summon_config.single_summon_cost.amount * 5
	print(f"  SkillSummonTickets={tickets}")
	print(f"  5x base cost={base_cost}")

	dry = logic.skill_summon(5, commit=False)
	print(f"\nDry-run count=5: {dry[0].name}")

	can_afford, _ = summon_config.can_afford_summon(player, 5)
	if not can_afford:
		currency.set_currency(CurrencyType.SkillSummonTickets, max(tickets, 100_000))

	tickets_before = currency.get(CurrencyType.SkillSummonTickets)
	seed_before = summon.seed
	level_before = summon.level
	count_before = summon.count
	skills_before = len(collection.player_skills)

	result, summoned = logic.skill_summon(5, commit=True)
	print(f"\n=== After summon (count=5) ===")
	print(f"  result={result.name}")
	print(f"  seed {seed_before:#018x} -> {summon.seed:#018x}")
	print(f"  level {level_before} -> {summon.level}")
	print(f"  count {count_before} -> {summon.count}")
	print(f"  skills {skills_before} -> {len(collection.player_skills)}")
	print(f"  summoned pulls={len(summoned)}")
	for info in summoned:
		skill = collection.try_get_skill(info.type)
		if skill is None:
			raise SystemExit(f"missing skill after summon: {info.type!r}")
		print(
			f"    {info.type.name}  new={info.is_new}  "
			f"shards={skill.shard_count}  lv={skill.level}"
		)

	tickets_after = currency.get(CurrencyType.SkillSummonTickets)
	cost = tickets_before - tickets_after
	print(f"  tickets spent={cost}")

	if result != ActionResult.Success:
		raise SystemExit(1)
	if summon.seed == seed_before:
		raise SystemExit("seed did not advance")
	print("\nOK")


if __name__ == "__main__":
	main()
