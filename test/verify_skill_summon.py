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
	dump_path = _ROOT / "test_user_dump.txt"
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
	print(f"  SkillSummonTickets={tickets}")

	# Dry-run validation
	dry = logic.skill_summon(5, commit=False)
	print(f"\nDry-run count=5: {dry[0].name}")

	# Ensure afford for test
	cost = player.game_config.skill_summon_config.single_summon_cost
	needed = cost.amount * 5
	if tickets < needed:
		currency.set_currency(cost.currency, needed)

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
		skill = collection.player_skills[info.type]
		print(
			f"    {info.type.name}  new={info.is_new}  "
			f"shards={skill.shard_count}  lv={skill.level}"
		)

	if result != ActionResult.Success:
		raise SystemExit(1)
	if summon.seed == seed_before:
		raise SystemExit("seed did not advance")
	print("\nOK")


if __name__ == "__main__":
	main()
