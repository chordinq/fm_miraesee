"""Verify EggSummonAction and MountSummonAction against dump summon meta state."""

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


def _ensure_currency(logic: GameLogic, currency: CurrencyType, count: int) -> None:
	player = logic.player
	currency_model = player.player_currency_model
	cost = None
	if currency == CurrencyType.Eggshells:
		cost = player.game_config.egg_summon_config.single_summon_cost
	elif currency == CurrencyType.ClockWinders:
		cost = player.game_config.mount_summon_config.single_summon_cost
	if cost is None:
		return
	needed = cost.amount * count
	if currency_model.get(currency) < needed:
		currency_model.set_currency(currency, needed)


def _verify_egg_summon(logic: GameLogic) -> None:
	player = logic.player
	collection = player.player_pet_collection_model
	summon = collection.summon_model
	currency = player.player_currency_model

	print("=== Egg summon ===")
	print(f"Before: seed={summon.seed:#018x} level={summon.level} count={summon.count} eggs={len(collection.eggs)}")
	print(f"  Eggshells={currency.get(CurrencyType.Eggshells)}")

	dry = logic.egg_summon(1, commit=False)
	print(f"Dry-run count=1: {dry[0].name}")

	_ensure_currency(logic, CurrencyType.Eggshells, 1)
	seed_before = summon.seed
	count_before = summon.count
	eggs_before = len(collection.eggs)

	result, summoned = logic.egg_summon(1, commit=True)
	print(f"After: result={result.name} seed {seed_before:#018x}->{summon.seed:#018x} count {count_before}->{summon.count} eggs {eggs_before}->{len(collection.eggs)}")
	for info in summoned:
		egg = info.egg_model
		print(f"  rarity={egg.rarity.name} seed={egg.seed:#018x} new={info.is_new} guid={egg.guid}")

	if result != ActionResult.Success:
		raise SystemExit("egg summon failed")
	if summon.seed == seed_before:
		raise SystemExit("egg seed did not advance")
	print("Egg OK\n")


def _verify_mount_summon(logic: GameLogic) -> None:
	player = logic.player
	collection = player.player_mount_collection_model
	summon = collection.summon_model
	currency = player.player_currency_model

	print("=== Mount summon ===")
	print(
		f"Before: seed={summon.seed:#018x} level={summon.level} count={summon.count} "
		f"mounts={len(collection.player_mount_models)}"
	)
	print(f"  ClockWinders={currency.get(CurrencyType.ClockWinders)}")

	dry = logic.mount_summon(1, commit=False)
	print(f"Dry-run count=1: {dry[0].name}")

	_ensure_currency(logic, CurrencyType.ClockWinders, 1)
	seed_before = summon.seed
	count_before = summon.count
	mounts_before = len(collection.player_mount_models)

	result, summoned = logic.mount_summon(1, commit=True)
	print(
		f"After: result={result.name} seed {seed_before:#018x}->{summon.seed:#018x} "
		f"count {count_before}->{summon.count} mounts {mounts_before}->{len(collection.player_mount_models)}"
	)
	for info in summoned:
		mid = info.mount_model.mount_id
		print(f"  mount={mid.rarity.name}/{mid.id} new={info.is_new} guid={info.mount_model.guid}")

	if result != ActionResult.Success:
		raise SystemExit("mount summon failed")
	if summon.seed == seed_before:
		raise SystemExit("mount seed did not advance")
	print("Mount OK")


def main() -> None:
	logic = _load_dump_player()
	_verify_egg_summon(logic)
	_verify_mount_summon(logic)
	print("\nAll OK")


if __name__ == "__main__":
	main()
