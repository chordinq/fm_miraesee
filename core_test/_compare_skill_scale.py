from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_item_stats import get_total_stats
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import ActiveSkillStatTarget
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def load(name: str):
    path = Path(__file__).resolve().parent / name
    return dump_snapshot_to_player_model(parse_dump_text(path.read_text(encoding="utf-8")))


def skill_scale(label: str, player):
    gc = player.game_config
    stats = get_total_stats(player)
    target = ActiveSkillStatTarget()
    from core.game_logic.stats.stat_helper import _NatureAccumulators

    acc = _NatureAccumulators(
        additive=stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Additive, target),
        multiplier=stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Multiplier, target),
        divisor=stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Divisor, target),
        one_minus=stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.OneMinusMultiplier, target),
    )
    for dep in (StatType.AscensionDamage, StatType.TechTreeDamage):
        StatHelper._accumulate_with_stat_deps(gc, stats, dep, target, acc)
    StatHelper._add_dependency_for_target(gc, stats, StatType.Damage, ActiveSkillStatTarget(skill_type=None), acc, None)

    result = (219.0 + acc.additive) * acc.multiplier * (1.0 - acc.one_minus) / acc.divisor
    print(f"=== {label} active-skill damage scale (base 219) ===")
    print(f"  add={acc.additive:.4f} mul={acc.multiplier:.6f} div={acc.divisor:.6f} 1-m={acc.one_minus:.6f}")
    print(f"  -> {result:.4f}  ({result/219*100-100:+.2f}% vs raw base)")
    print()


for name, label in [("_old_dump.txt", "OLD"), ("test_user_dump.txt", "NEW")]:
    skill_scale(label, load(name))
