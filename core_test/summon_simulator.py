from __future__ import annotations

import copy
from dataclasses import dataclass, field

from core.game_logic.actions import ActionResult, MetaActionResult
from core.game_logic.actions.summon.skill_summon_action import (
	SummonedSkillInfo,
	_skills_for_rarity,
)
from core.game_logic.enums import CurrencyType, StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import ActiveSkillStatTarget
from core.game_logic.summon_config import SummonConfig
from core.miraesee_extension import miraesee_extension
from core.random_pcg import RandomPCG


@dataclass(frozen=True)
class SummonPullLedger:
	pull_index: int
	summon_count: int
	cost: int
	tickets_before: int
	tickets_after: int
	overdraft: bool
	deficit_at_pull: int
	cumulative_spent: int
	cumulative_deficit: int


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
def resolved_summon_cost(
	player: PlayerModel,
	summon_config: SummonConfig,
	summon_count: int,
) -> int:
	base_amount = summon_config.single_summon_cost.amount * summon_count
	target = summon_config.summonable_id.get_stat_target()
	return round(
		StatHelper.calculate_value(
			player,
			StatType.Cost,
			target,
			base_amount,
		)
	)


def _run_skill_summon_rolls(
	player: PlayerModel,
	summon_count: int,
) -> tuple[MetaActionResult, list[SummonedSkillInfo]]:
	game_config = player.game_config
	summon_config = game_config.skill_summon_config
	collection = player.player_skill_collection_model
	summon_model = collection.summon_model
	summoned: list[SummonedSkillInfo] = []

	freebie_target = ActiveSkillStatTarget()
	effective_count = summon_count
	i = 0
	while i < effective_count:
		rng = RandomPCG.create_from_seed(summon_model.seed)
		if i < summon_count:
			if StatHelper.roll_stat(
				player,
				StatType.FreebieChance,
				freebie_target,
				rng,
			):
				effective_count += 1

		level_cfg = summon_config.levels[summon_model.level]
		rolled_rarity = level_cfg.roll_rarity(rng)
		candidates = _skills_for_rarity(game_config.skill_library, rolled_rarity)
		if not candidates:
			return ActionResult.DoesNotExist, summoned

		combat_skill = rng.choice(iter(candidates))
		existing = collection.player_skills.get(combat_skill)
		if existing is None:
			skill = PlayerSkillModel(combat_skill)
			collection.player_skills[combat_skill] = skill
			summoned.append(SummonedSkillInfo(skill, True))
		else:
			existing.add_shards(1, None)
			summoned.append(SummonedSkillInfo(existing, False))

		summon_model.increment_summon_count(summon_config)
		i += 1

	if any(info.is_new for info in summoned):
		player.player_power_model.update_power(player, publish_update=False)

	return ActionResult.Success, summoned


@miraesee_extension
def skill_summon_allow_overdraft(
	logic: GameLogic,
	summon_count: int,
	*,
	commit: bool = True,
	pull_index: int = 1,
	tickets_at_start: int | None = None,
	cumulative_spent_before: int = 0,
) -> tuple[MetaActionResult, list[SummonedSkillInfo], SummonPullLedger | None]:
	player = logic.player
	summon_config = player.game_config.skill_summon_config
	currency = summon_config.single_summon_cost.currency

	if summon_count not in summon_config.possible_summon_count:
		return ActionResult.DoesNotExist, [], None

	cost = resolved_summon_cost(player, summon_config, summon_count)
	tickets_before = player.player_currency_model.get(currency)
	if tickets_at_start is None:
		tickets_at_start = tickets_before

	deficit_at_pull = max(0, cost - tickets_before)
	overdraft = deficit_at_pull > 0
	cumulative_spent = cumulative_spent_before + cost
	cumulative_deficit = max(0, cumulative_spent - tickets_at_start)

	if not commit:
		ledger = SummonPullLedger(
			pull_index=pull_index,
			summon_count=summon_count,
			cost=cost,
			tickets_before=tickets_before,
			tickets_after=tickets_before - cost,
			overdraft=overdraft,
			deficit_at_pull=deficit_at_pull,
			cumulative_spent=cumulative_spent,
			cumulative_deficit=cumulative_deficit,
		)
		return ActionResult.Success, [], ledger

	spend_context = player.player_currency_model.create_spend_context(
		player,
		currency,
		cost,
	)
	spend_context.spend("SkillSummon")

	result, summoned = _run_skill_summon_rolls(player, summon_count)
	tickets_after = player.player_currency_model.get(currency)
	ledger = SummonPullLedger(
		pull_index=pull_index,
		summon_count=summon_count,
		cost=cost,
		tickets_before=tickets_before,
		tickets_after=tickets_after,
		overdraft=overdraft,
		deficit_at_pull=deficit_at_pull,
		cumulative_spent=cumulative_spent,
		cumulative_deficit=cumulative_deficit,
	)
	return result, summoned, ledger


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
