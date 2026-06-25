from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.shared_game_config import SharedGameConfig
from core.game_logic.skill_builder import get_skill_damage_count
from core.game_logic.skill_description import _sum_active_damage_health, format_skill_description_args
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def load(name: str):
    path = Path(__file__).resolve().parent / name
    return dump_snapshot_to_player_model(parse_dump_text(path.read_text(encoding="utf-8")))


def shout_breakdown(label: str, player):
    gc = player.game_config
    skill = next(s for s in player.player_skill_collection_model.get_player_skills() if int(s.type) == 4)
    total = get_total_stats(player)
    base = SharedGameConfig.get_base_active_skill_stats(gc, skill.type, skill.level)
    resolved = SharedGameConfig.get_resolved_active_skill_stats(gc, skill.type, skill.level, total)
    dmg, hp = _sum_active_damage_health(resolved)
    hits = get_skill_damage_count(skill.type)
    print(f"--- {label} Shout Lv{skill.level + 1} ---")
    print(f"  format args: {format_skill_description_args(player, skill)}")
    print(f"  resolved total damage: {dmg:.4f}  per hit: {dmg / hits:.4f}")
    print(f"  base contributions (non-zero):")
    for node, raw in base.stats.items():
        if raw == 0:
            continue
        incoming = raw / 1_000_000
        resolved_val = resolved.all_stat_contributions.get(node, 0)
        print(
            f"    {node.unique_stat.stat_type.name} "
            f"raw_fd6={raw} incoming={incoming:.4f} -> resolved={resolved_val:.4f}"
        )


def main():
    shout_breakdown("OLD", load("_old_dump.txt"))
    shout_breakdown("NEW", load("test_user_dump.txt"))


if __name__ == "__main__":
    main()
