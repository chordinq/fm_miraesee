from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from config import SKILLS_MAPPING
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id
from core.game_logic.skill_builder import get_skill_damage_count
from core.game_logic.skill_description import format_skill_description_args
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def skill_key(skill) -> str:
    sid = combat_skill_to_skill_id(skill.type)
    return SKILLS_MAPPING[f"{sid.rarity.value}_{sid.idx}"]["Key"]


def load(path: Path):
    return dump_snapshot_to_player_model(parse_dump_text(path.read_text(encoding="utf-8")))


def report(label: str, player) -> dict[str, tuple[int, list[str]]]:
    stats = get_total_stats(player)
    gc = player.game_config
    print(f"=== {label} ===")
    print(f"  player damage (melee): {stats.player_damage(gc, False):.2f}")
    print(f"  player damage (ranged): {stats.player_damage(gc, True):.2f}")
    print(f"  player health: {stats.player_health(gc):.2f}")
    out = {}
    for skill in player.player_skill_collection_model.get_player_skills():
        key = skill_key(skill)
        args = format_skill_description_args(player, skill)
        hits = get_skill_damage_count(skill.type)
        out[key] = (skill.level + 1, args)
        print(f"  {key:<16} Lv{skill.level + 1:>3}  hits={hits}  args={args}")
    print()
    return out


def main() -> None:
    base = Path(__file__).resolve().parent
    old_path = base / "_old_dump.txt"
    new_path = base / "test_user_dump.txt"
    old = report("OLD", load(old_path))
    new = report("NEW", load(new_path))
    print("=== DELTA (NEW vs OLD) ===")
    for key in sorted(set(old) | set(new)):
        if key not in old or key not in new:
            print(f"  {key}: missing in one dump")
            continue
        olv, oargs = old[key]
        nlv, nargs = new[key]
        if olv != nlv or oargs != oargs:
            print(f"  {key}: Lv {olv}->{nlv}  args {oargs} -> {nargs}")


if __name__ == "__main__":
    main()
