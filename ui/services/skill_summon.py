# ui/services/skill_summon.py — skill summon UI display helpers + error translation wrapper
from __future__ import annotations

import dataclasses

from features.summon.skill_summon import (  # noqa: F401 (re-export)
    SkillSummonSessionResult,
    available_batch_sizes,
    skill_model_for_pull,
    summon_batch_cost,
    summon_ticket_balance,
)
from features.summon.skill_summon import (
    run_skill_summon_session as _features_run_skill_summon_session,
)
from features.summon.skill_summon import (
    summon_level_progress as _features_summon_level_progress,
)
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.summon_base import SummonPullResult
from ui.services.display_level import format_level
from ui.services.localization import rarity_display_name, skill_display_name, ui_text


def summon_level_progress(player: PlayerModel) -> tuple[str, int, int]:
    """Return (Lv. label, current count, required for next level)."""
    level, cur, req = _features_summon_level_progress(player)
    return format_level(level), cur, req


def pull_skill_label(pull: SummonPullResult) -> str:
    skill = skill_model_for_pull(pull)
    if skill is not None:
        return skill_display_name(skill)
    return pull.detail


def pull_result_line(pull: SummonPullResult) -> str:
    rarity = rarity_display_name(pull.rarity)
    name = pull_skill_label(pull)
    tag = ui_text("summon_new") if pull.is_new else ui_text("summon_shard")
    return f"[{rarity}] {name} — {tag}"


def run_skill_summon_session(
    player: PlayerModel,
    *,
    batch_size: int,
    repeat_count: int,
) -> SkillSummonSessionResult:
    """Run the summon session and translate any error key to display text."""
    result = _features_run_skill_summon_session(
        player,
        batch_size=batch_size,
        repeat_count=repeat_count,
    )
    if result.error is not None:
        translated = ui_text(result.error)
        result = dataclasses.replace(result, error=translated if translated != result.error else result.error)
    return result
