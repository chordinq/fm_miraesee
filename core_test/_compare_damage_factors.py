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


def damage_factors(label: str, player):
    gc = player.game_config
    stats = get_total_stats(player)
    shout_target = ActiveSkillStatTarget(skill_type=player.player_skill_collection_model.get_player_skills()[2].type)
    player_target = PlayerStatTarget()

    def row(name, target):
        add = stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Additive, target)
        mul = stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Multiplier, target)
        div = stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.Divisor, target)
        om = stats.get_stat_value_or_default(gc, StatType.Damage, StatNature.OneMinusMultiplier, target)
        resolved = (219.0 + add) * mul * (1.0 - om) / div
        print(f"  {name}: add={add:.4f} mul={mul:.6f} div={div:.6f} 1-m={om:.6f} -> scale(219)={resolved:.4f}")

    print(f"=== {label} ===")
    row("PlayerStatTarget", player_target)
    row("ActiveSkill(Shout)", shout_target)
    print()


for name, label in [("_old_dump.txt", "OLD"), ("test_user_dump.txt", "NEW")]:
    damage_factors(label, load(name))
