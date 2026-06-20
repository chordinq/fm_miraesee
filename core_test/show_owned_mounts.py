"""Show mounts from test_user_dump.txt with Mounts_Mapping names."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from core.game_logic.enums import Rarity, SecondaryStatType
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


def _mount_key_name(mapping: dict, rarity: Rarity, idx: int) -> str:
	row = mapping.get(f"{rarity.value}_{idx}")
	return row["Key"] if row else f"??? ({rarity.value}_{idx})"


def main() -> None:
	mapping = json.loads((_ROOT / "config" / "Mounts_Mapping.json").read_text(encoding="utf-8"))
	text = (_ROOT / "test_user_dump.txt").read_text(encoding="utf-8")
	player = dump_snapshot_to_player_model(parse_dump_text(text))
	game_config = player.game_config
	collection = player.player_mount_collection_model

	print("=== 보유 Mount (덤프 기준) ===")
	print(f"총 {len(collection.player_mount_models)}마리\n")

	for i, mount in enumerate(collection.player_mount_models):
		mid = mount.mount_id
		name = _mount_key_name(mapping, mid.rarity, mid.id)
		stats = mount.secondary_stats
		stat_lines: list[str] = []
		for stat_type in sorted(stats.interpolated_stat_values, key=lambda x: x.value):
			ok, value = stats.try_get_stat_value(stat_type, game_config)
			if ok:
				stat_lines.append(f"{_STAT_NAMES[stat_type]} (+{value * 100:.2f}%)")

		equipped = " [장착]" if mount.is_equipped else ""
		print(f"[{i}] {mid.rarity.name} #{mid.id} → {name}{equipped}")
		print(
			f"    L={mount.level} (표시 L{mount.level + 1}) | "
			f"xp={mount.experience} | total_xp={mount.get_total_xp(player)}"
		)
		for j, line in enumerate(stat_lines, 1):
			print(f"    stat{j}: {line}")
		print(f"    perfection={stats.perfection * 100}%")
		print()


if __name__ == "__main__":
	main()
