"""Offline batch summon simulation helpers."""
from __future__ import annotations

import copy
from dataclasses import dataclass, field

from core.game_logic.actions import ActionResult, MetaActionResult
from core.game_logic.actions.summon.skill_summon_action import SummonedSkillInfo
from core.game_logic.enums import CurrencyType
from core.game_logic.game_logic import GameLogic
from core.miraesee_extension import miraesee_extension
from utils.summon.overdraft import SummonPullLedger, skill_summon_allow_overdraft

__all__ = [
	"SummonBatchResult",
	"simulate_skill_summon_batch",
]


@dataclass
class SummonBatchResult:
	tickets_at_start: int
	tickets_at_end: int
	total_spent: int
	total_deficit: int
	pulls: list[SummonPullLedger] = field(default_factory=list)
	summoned: list[SummonedSkillInfo] = field(default_factory=list)
	stopped_early: MetaActionResult | None = None


@miraesee_extension
def simulate_skill_summon_batch(
	logic: GameLogic,
	summon_count: int,
	num_pulls: int,
	*,
	use_copy: bool = True,
) -> SummonBatchResult:
	if num_pulls < 1:
		raise ValueError("num_pulls must be at least 1")

	if use_copy:
		player = copy.deepcopy(logic.player)
		sim_logic = GameLogic(player)
	else:
		sim_logic = logic
		player = sim_logic.player

	tickets_at_start = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
	batch = SummonBatchResult(
		tickets_at_start=tickets_at_start,
		tickets_at_end=tickets_at_start,
		total_spent=0,
		total_deficit=0,
	)

	cumulative_spent = 0
	for pull_index in range(1, num_pulls + 1):
		result, summoned, ledger = skill_summon_allow_overdraft(
			sim_logic,
			summon_count,
			commit=True,
			pull_index=pull_index,
			tickets_at_start=tickets_at_start,
			cumulative_spent_before=cumulative_spent,
		)
		if ledger is None:
			batch.stopped_early = result
			break

		batch.pulls.append(ledger)
		batch.summoned.extend(summoned)
		cumulative_spent = ledger.cumulative_spent

		if result != ActionResult.Success:
			batch.stopped_early = result
			break

	batch.tickets_at_end = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
	batch.total_spent = tickets_at_start - batch.tickets_at_end
	batch.total_deficit = max(0, batch.total_spent - tickets_at_start)
	return batch
