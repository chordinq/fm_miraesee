"""Print skill passive base/resolved damage and health from test_user_dump.txt."""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from config import SKILLS_MAPPING
from core.game_logic.enums import Rarity, StatNature, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id
from core.game_logic.shared_game_config import SharedGameConfig, _get_skill_rarity
from core.game_logic.stats.stats import Stats
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


@dataclass(frozen=True)
class PassiveStatRow:
	key: str
	rarity: Rarity
	level: int
	config_damage: float
	config_health: float
	resolved_damage: float
	resolved_health: float


def _skill_key(combat_skill) -> str:
	skill_id = combat_skill_to_skill_id(combat_skill)
	return SKILLS_MAPPING[f"{skill_id.rarity.value}_{skill_id.idx}"]["Key"]


def _config_passive_base(
	game_config,
	rarity: Rarity,
	level: int,
) -> tuple[float, float]:
	passive_config = game_config.skill_passive_library.get(rarity)
	if passive_config is None:
		raise ValueError(f"No passive config for rarity: {rarity!r}")

	level_stats_list = passive_config.get("LevelStats", [])
	if level >= len(level_stats_list):
		return 0.0, 0.0

	damage = 0.0
	health = 0.0
	for row in level_stats_list[level].get("Stats", []):
		stat_type = row["StatNode"]["UniqueStat"]["StatType"]
		value = float(row["Value"])
		if stat_type == "Damage":
			damage = value
		elif stat_type == "Health":
			health = value
	return damage, health


def _sum_additive_damage_health(resolved: Stats) -> tuple[float, float]:
	damage = 0.0
	health = 0.0
	for node, value in resolved.all_stat_contributions.items():
		if node.unique_stat.stat_nature != StatNature.Additive:
			continue
		if node.unique_stat.stat_type == StatType.Damage:
			damage += value
		elif node.unique_stat.stat_type == StatType.Health:
			health += value
	return damage, health


def collect_passive_rows(player) -> list[PassiveStatRow]:
	game_config = player.game_config
	total_stats = get_total_stats(player)
	collection = player.player_skill_collection_model
	rows: list[PassiveStatRow] = []

	for skill in sorted(
		collection.player_skills.values(),
		key=lambda s: (
			_get_skill_rarity(game_config, s.type).value,
			s.type.value,
		),
	):
		rarity = _get_skill_rarity(game_config, skill.type)
		config_damage, config_health = _config_passive_base(game_config, rarity, skill.level)
		resolved = SharedGameConfig.get_resolved_passive_skill_stats(
			game_config,
			skill.type,
			skill.level,
			total_stats,
		)
		resolved_damage, resolved_health = _sum_additive_damage_health(resolved)
		rows.append(
			PassiveStatRow(
				key=_skill_key(skill.type),
				rarity=rarity,
				level=skill.level,
				config_damage=config_damage,
				config_health=config_health,
				resolved_damage=resolved_damage,
				resolved_health=resolved_health,
			)
		)
	return rows


def main() -> None:
	dump_path = Path(__file__).resolve().parent / "test_user_dump.txt"
	player = dump_snapshot_to_player_model(parse_dump_text(dump_path.read_text(encoding="utf-8")))
	rows = collect_passive_rows(player)

	print("=== Skill passive damage / health (dump) ===")
	print(f"source: {dump_path.name}")
	print(f"skills: {len(rows)}")
	print()
	print(
		f"{'Skill':<16} {'Rarity':<10} {'Lv':>3}  "
		f"{'cfg dmg':>8} {'cfg hp':>8}  "
		f"{'res dmg':>8} {'res hp':>8}"
	)
	print("-" * 72)

	total_cfg_damage = 0.0
	total_cfg_health = 0.0
	total_res_damage = 0.0
	total_res_health = 0.0
	for row in rows:
		total_cfg_damage += row.config_damage
		total_cfg_health += row.config_health
		total_res_damage += row.resolved_damage
		total_res_health += row.resolved_health
		print(
			f"{row.key:<16} {row.rarity.name:<10} {row.level + 1:>3}  "
			f"{row.config_damage:>8.1f} {row.config_health:>8.1f}  "
			f"{row.resolved_damage:>8.2f} {row.resolved_health:>8.2f}"
		)

	print("-" * 72)
	print(
		f"{'TOTAL':<16} {'':<10} {'':>3}  "
		f"{total_cfg_damage:>8.1f} {total_cfg_health:>8.1f}  "
		f"{total_res_damage:>8.2f} {total_res_health:>8.2f}"
	)
	print()
	print("cfg  = SkillPassiveLibrary Value (level row)")
	print("res  = get_resolved_passive_skill_stats (player total stats applied)")


if __name__ == "__main__":
	main()
