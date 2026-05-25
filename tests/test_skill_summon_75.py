# tests/test_skill_summon_75.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.game_logic.player_model.PlayerModel import PlayerModel
from core.enums import CurrencyType
from core.game_logic.GameLogic import GameLogic

EXPECTED = [
	"CannonBarrage", "Shuriken", "Berserk", "Berserk", "Meat", "Shuriken", "Meat", "Meat",
	"Shuriken", "Berserk", "Thorns", "CannonBarrage", "Berserk", "Bomb", "CannonBarrage",
	"Berserk", "CannonBarrage", "Meat", "Shuriken", "Shuriken", "Shuriken", "CannonBarrage",
	"Berserk", "Shout", "Berserk", "Berserk", "Berserk", "Shuriken", "Berserk", "Shuriken",
	"Shuriken", "Shuriken", "Berserk", "Shout", "CannonBarrage", "CannonBarrage", "Arrows",
	"Meat", "Shuriken", "Shout", "Berserk", "Buff", "CannonBarrage", "Shuriken", "Berserk",
	"Meat", "RainOfArrows", "CannonBarrage", "Berserk", "Morale", "Berserk", "CannonBarrage",
	"Shuriken", "Berserk", "Shuriken", "Thorns", "Berserk", "Shuriken", "Arrows",
	"CannonBarrage", "Shuriken", "Shuriken", "Berserk", "Shuriken", "Arrows", "Meat",
	"Berserk", "Shuriken", "Berserk", "CannonBarrage", "Shuriken", "Arrows", "Shuriken",
	"CannonBarrage", "Shuriken",
]


def _norm(name: str) -> str:
	return name.replace(" ", "")


def main():
	player = PlayerModel()
	player.currency.set_currency(CurrencyType.SkillSummonTickets, 999_999)
	sm = player.skills.summon_model
	sm.level = 22
	sm.count = 54
	sm.set_seed(0x9665DD1A85C3340D)

	result = GameLogic(player).summon_skills(75)
	got = [_norm(p.detail) for p in result.pulls]

	mismatches = [
		(i + 1, EXPECTED[i], got[i])
		for i in range(min(len(EXPECTED), len(got)))
		if EXPECTED[i] != got[i]
	]

	print(f"pulls: {len(got)} (expected {len(EXPECTED)})")
	print(f"mismatches: {len(mismatches)}")
	for row in mismatches[:20]:
		print(f"  #{row[0]}: expected {row[1]!r} got {row[2]!r}")
	if not mismatches:
		print("ALL MATCH")
	print(f"final seed: {sm.get_seed():#018x}  count: {sm.count}  level: {sm.level}")


if __name__ == "__main__":
	main()
