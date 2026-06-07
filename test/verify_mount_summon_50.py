"""Verify mount summon x50 against in-game reference table."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType, Rarity, SecondaryStatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.shared_game_config import SharedGameConfig
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

_STAT_NAMES: dict[SecondaryStatType, str] = {
	SecondaryStatType.CriticalChance: "Critical Chance",
	SecondaryStatType.CriticalMulti: "Critical Damage",
	SecondaryStatType.BlockChance: "Block Chance",
	SecondaryStatType.HealthRegen: "Health Regen",
	SecondaryStatType.LifeSteal: "Life Steal",
	SecondaryStatType.DoubleDamageChance: "Double Chance",
	SecondaryStatType.DamageMulti: "Damage",
	SecondaryStatType.MeleeDamageMulti: "Melee Damage",
	SecondaryStatType.RangedDamageMulti: "Ranged Damage",
	SecondaryStatType.AttackSpeed: "Attack Speed",
	SecondaryStatType.SkillDamageMulti: "Skill Damage",
	SecondaryStatType.SkillCooldownMulti: "Skill Cooldown",
	SecondaryStatType.HealthMulti: "Health",
}

_RARITY_KO: dict[Rarity, str] = {
	Rarity.Common: "일반",
	Rarity.Rare: "희귀",
}

# In-game reference (user-provided): tier, stat1 label, perfection%
EXPECTED: list[tuple[str, str, float]] = [
	("희귀", "Critical Damage (+78.46%)", 98.05),
	("일반", "Skill Damage (+26.66%)", 88.50),
	("일반", "Attack Speed (+3.60%)", 6.66),
	("일반", "Block Chance (+3.26%)", 56.40),
	("일반", "Critical Damage (+42.79%)", 52.90),
	("희귀", "Melee Damage (+37.48%)", 74.45),
	("일반", "Attack Speed (+12.02%)", 28.26),
	("희귀", "Life Steal (+17.28%)", 85.71),
	("일반", "Critical Damage (+54.78%)", 68.08),
	("희귀", "Health Regen (+1.51%)", 16.85),
	("희귀", "Melee Damage (+1.26%)", 0.53),
	("희귀", "Attack Speed (+2.72%)", 4.41),
	("희귀", "Melee Damage (+26.27%)", 51.57),
	("희귀", "Block Chance (+4.22%)", 80.47),
	("희귀", "Block Chance (+4.17%)", 79.20),
	("희귀", "Life Steal (+17.24%)", 85.46),
	("희귀", "Critical Damage (+48.97%)", 60.72),
	("희귀", "Skill Damage (+23.92%)", 79.04),
	("희귀", "Block Chance (+4.70%)", 92.54),
	("희귀", "Block Chance (+3.71%)", 67.71),
	("일반", "Ranged Damage (+3.12%)", 15.17),
	("희귀", "Ranged Damage (+14.27%)", 94.82),
	("희귀", "Critical Damage (+53.49%)", 66.44),
	("일반", "Block Chance (+3.36%)", 58.89),
	("일반", "Melee Damage (+31.72%)", 62.70),
	("희귀", "Health (+5.06%)", 29.01),
	("일반", "Critical Chance (+3.75%)", 24.98),
	("일반", "Ranged Damage (+13.59%)", 89.94),
	("일반", "Critical Chance (+7.64%)", 60.40),
	("희귀", "Ranged Damage (+4.45%)", 24.62),
	("희귀", "Critical Chance (+1.23%)", 2.11),
	("희귀", "Critical Damage (+22.08%)", 26.69),
	("희귀", "Health Regen (+2.00%)", 33.47),
	("희귀", "Life Steal (+5.18%)", 22.02),
	("희귀", "Attack Speed (+6.69%)", 14.58),
	("희귀", "Skill Cooldown (+6.83%)", 97.22),
	("일반", "Damage (+10.09%)", 64.90),
	("희귀", "Block Chance (+1.47%)", 11.87),
	("희귀", "Skill Cooldown (+5.52%)", 75.30),
	("희귀", "Double Chance (+11.22%)", 53.78),
	("희귀", "Health (+12.26%)", 80.42),
	("희귀", "Life Steal (+12.78%)", 61.98),
	("희귀", "Attack Speed (+17.20%)", 41.54),
	("희귀", "Double Chance (+11.76%)", 56.65),
	("희귀", "Critical Damage (+45.19%)", 55.94),
	("희귀", "Life Steal (+10.25%)", 48.66),
	("희귀", "Health Regen (+2.10%)", 36.61),
	("희귀", "Skill Cooldown (+1.61%)", 10.09),
	("일반", "Double Chance (+1.28%)", 1.49),
	("희귀", "Block Chance (+4.11%)", 77.73),
	("희귀", "Health (+10.80%)", 69.99),
	("희귀", "Skill Damage (+26.03%)", 86.30),
	("희귀", "Health Regen (+1.27%)", 9.13),
	("희귀", "Double Chance (+17.47%)", 86.71),
	("일반", "Block Chance (+1.40%)", 10.01),
	("희귀", "Health (+9.45%)", 60.32),
	("일반", "Critical Damage (+26.76%)", 32.61),
	("희귀", "Block Chance (+1.88%)", 21.90),
	("희귀", "Health (+2.03%)", 7.33),
	("희귀", "Melee Damage (+46.09%)", 92.02),
]


def _fmt_mount(mount, game_config: SharedGameConfig) -> tuple[str, str, float]:
	stats = mount.secondary_stats
	stat_parts: list[str] = []
	for stat_type in sorted(stats.interpolated_stat_values, key=lambda x: x.value):
		ok, value = stats.try_get_stat_value(stat_type, game_config)
		if ok:
			stat_parts.append(
				f"{_STAT_NAMES[stat_type]} (+{value * 100:.2f}%)"
			)
	tier = _RARITY_KO.get(mount.mount_id.rarity, mount.mount_id.rarity.name)
	stat1 = stat_parts[0] if stat_parts else "-"
	perf = stats.perfection * 100
	return tier, stat1, perf


def _matches_expected(
	got: tuple[str, str, float],
	exp: tuple[str, str, float],
	*,
	perfection_tol: float = 0.01,
) -> bool:
	tier_ok = got[0] == exp[0]
	stat_ok = got[1] == exp[1]
	# Reference table uses UI-rounded perfection; allow small display-rounding delta.
	perf_ok = abs(got[2] - exp[2]) <= perfection_tol
	return tier_ok and stat_ok and perf_ok


def main() -> None:
	dump_path = _ROOT / "test_user_dump.txt"
	text = dump_path.read_text(encoding="utf-8")
	logic = GameLogic(dump_snapshot_to_player_model(parse_dump_text(text)))
	player = logic.player
	game_config = player.game_config
	summon = player.player_mount_collection_model.summon_model
	currency = player.player_currency_model

	print("=== Mount summon x50 verification ===")
	print(
		f"Before: seed={summon.seed:#018x} level={summon.level} count={summon.count} "
		f"ClockWinders={currency.get(CurrencyType.ClockWinders):,}"
	)

	result, summoned = logic.mount_summon(50, commit=True)
	print(
		f"Result: {result.name} | summoned={len(summoned)} | "
		f"seed_after={summon.seed:#018x} | CW left={currency.get(CurrencyType.ClockWinders):,}"
	)

	if result != ActionResult.Success:
		raise SystemExit(1)
	if len(summoned) != len(EXPECTED):
		print(f"COUNT MISMATCH: got {len(summoned)}, expected {len(EXPECTED)}")

	mismatches = 0
	for i, (info, exp) in enumerate(zip(summoned, EXPECTED), start=1):
		got = _fmt_mount(info.mount_model, game_config)
		if not _matches_expected(got, exp):
			mismatches += 1
			print(f"MISMATCH #{i}")
			print(f"  expected: {exp}")
			print(f"  got:      {got}")

	if mismatches == 0 and len(summoned) == len(EXPECTED):
		print(f"All {len(EXPECTED)} mounts match in-game reference.")
	else:
		print(f"{mismatches} mismatches out of {min(len(summoned), len(EXPECTED))}")
		# Show first 10 got vs expected for debugging
		print("\nFirst 10 comparison:")
		for i in range(min(10, len(summoned), len(EXPECTED))):
			got = _fmt_mount(summoned[i].mount_model, game_config)
			print(f"  [{i+1}] exp={EXPECTED[i]}")
			print(f"       got={got}")
		sys.exit(1)


if __name__ == "__main__":
	main()
