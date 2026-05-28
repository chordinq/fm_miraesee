# features/summon/skill_summon.py — skill summon use case
# error field stores a localization key (e.g. "summon_no_tickets"), not display text.
from __future__ import annotations

from dataclasses import dataclass, field

from configs import SKILL_MAPPING, SKILL_SUMMON_CONFIG
from core.enums import Rarity, TechTreeNodeType
from core.game_logic.GameLogic import GameLogic
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel
from core.game_logic.summon_base import SummonPullResult, SummonResult
from core.game_logic.summon_cost import can_afford_summon_batch, effective_batch_ticket_cost


@dataclass
class SkillSummonSessionResult:
    batch_size: int
    repeat_count: int
    pulls: list[SummonPullResult] = field(default_factory=list)
    success: bool = True
    error: str | None = None
    """Localization key for error message, e.g. 'summon_no_tickets'. Translate in UI layer."""


def available_batch_sizes(player: PlayerModel) -> list[int]:
    """PossibleSummonCount entries unlocked for this player."""
    config = SKILL_SUMMON_CONFIG
    counts = list(config.possible_summon_count)
    if not counts:
        return [5]
    if len(counts) == 1 or config.can_unlock_bulk(player):
        return counts
    return [counts[0]]


def summon_ticket_balance(player: PlayerModel) -> int:
    return player.get_currency(SKILL_SUMMON_CONFIG.currency_type)


def summon_batch_cost(player: PlayerModel, batch_size: int) -> int:
    """Ticket cost for one batch (includes SkillSummonCost tech discount)."""
    return effective_batch_ticket_cost(
        player,
        SKILL_SUMMON_CONFIG,
        TechTreeNodeType.SkillSummonCost,
        batch_size,
    )


def summon_level_progress(player: PlayerModel) -> tuple[int, int, int]:
    """Return (level, current count, required for next level)."""
    sm = player.skills.summon_model
    level_cfg = SKILL_SUMMON_CONFIG.get_level_config(sm.level)
    return sm.level, sm.count, level_cfg.summons_required


def skill_model_for_pull(pull: SummonPullResult) -> SkillModel | None:
    """Resolve a SummonPullResult to a SkillModel if possible."""
    for data in SKILL_MAPPING.values():
        name = str(data.get("Name", ""))
        compact = name.replace(" ", "")
        if compact == pull.detail or name == pull.detail:
            return SkillModel(Rarity(int(data["Rarity"])), int(data["Idx"]))
    return None


def run_skill_summon_session(
    player: PlayerModel,
    *,
    batch_size: int,
    repeat_count: int,
) -> SkillSummonSessionResult:
    """Execute repeated skill summons. Returns result with error as a localization key."""
    config = SKILL_SUMMON_CONFIG
    if batch_size not in config.possible_summon_count:
        return SkillSummonSessionResult(
            batch_size, repeat_count, success=False, error="summon_invalid_count"
        )

    batch_cost = summon_batch_cost(player, batch_size)
    total_cost = batch_cost * repeat_count
    if summon_ticket_balance(player) < total_cost:
        return SkillSummonSessionResult(
            batch_size,
            repeat_count,
            success=False,
            error="summon_no_tickets",
        )

    gl = GameLogic(player)
    pulls: list[SummonPullResult] = []
    for _ in range(repeat_count):
        if not can_afford_summon_batch(
            player, config, TechTreeNodeType.SkillSummonCost, batch_size
        ):
            return SkillSummonSessionResult(
                batch_size,
                repeat_count,
                pulls=pulls,
                success=False,
                error="summon_no_tickets",
            )
        result: SummonResult = gl.summon_skills(batch_size)
        if not result.success:
            return SkillSummonSessionResult(
                batch_size,
                repeat_count,
                pulls=pulls,
                success=False,
                error=result.error or "summon_failed",
            )
        pulls.extend(result.pulls)

    return SkillSummonSessionResult(batch_size, repeat_count, pulls=pulls)
