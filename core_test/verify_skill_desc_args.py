"""Print FormatSkillDescription args per owned skill from test_user_dump.txt."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from config import SKILLS_MAPPING
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id
from core.game_logic.skill_builder import get_skill_damage_count
from core.game_logic.skill_description import format_skill_description_args
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def _skill_key(combat_skill) -> str:
	skill_id = combat_skill_to_skill_id(combat_skill)
	return SKILLS_MAPPING[f"{skill_id.rarity.value}_{skill_id.idx}"]["Key"]


def main() -> None:
	dump_path = Path(__file__).resolve().parent / "test_user_dump.txt"
	player = dump_snapshot_to_player_model(parse_dump_text(dump_path.read_text(encoding="utf-8")))
	collection = player.player_skill_collection_model

	print(f"source: {dump_path.name}")
	print()
	for skill in collection.get_player_skills():
		key = _skill_key(skill.type)
		hits = get_skill_damage_count(skill.type)
		args = format_skill_description_args(player, skill)
		print(
			f"{key:<16} Lv{skill.level + 1:>3}  "
			f"hits={hits}  args={args}"
		)


if __name__ == "__main__":
	main()
