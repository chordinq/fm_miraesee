from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.stats.stat_target import ActiveSkillStatTarget, PlayerStatTarget
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def load(name: str):
    path = Path(__file__).resolve().parent / name
    return dump_snapshot_to_player_model(parse_dump_text(path.read_text(encoding="utf-8")))


def show(label: str, player):
    gc = player.game_config
    stats = get_total_stats(player)
    targets = [
        ("Player", PlayerStatTarget()),
        ("ActiveSkill(all)", ActiveSkillStatTarget()),
    ]
    types = [
        StatType.Damage,
        StatType.AscensionDamage,
        StatType.TechTreeDamage,
    ]
    print(f"=== {label} ===")
    for tname, target in targets:
        print(f"  [{tname}]")
        for st in types:
            for nat in (StatNature.Additive, StatNature.Multiplier):
                v = stats.get_stat_value_or_default(gc, st, nat, target)
                default = stats.get_stat_default_value(gc, st, nat)
                if abs(v - default) > 1e-6:
                    print(f"    {st.name}/{nat.name}: {v:.6f} (def {default:.6f})")
    print()


for name, label in [("_old_dump.txt", "OLD"), ("test_user_dump.txt", "NEW")]:
    show(label, load(name))
