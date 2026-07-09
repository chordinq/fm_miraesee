"""Summon overdraft execution used by the UI (negative-currency dev mode)."""
from __future__ import annotations

from dataclasses import dataclass

from core.game_logic.actions import ActionResult, MetaActionResult
from core.game_logic.actions.summon.egg_summon_action import SummonedEggInfo
from core.game_logic.actions.summon.mount_summon_action import (
	SummonedMountsInfo,
	_mount_ids_for_rarity,
)
from core.game_logic.actions.summon.skill_summon_action import (
	SummonedSkillInfo,
	_skills_for_rarity,
)
from core.game_logic.enums import StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_mount_collection_model import create_mount_from_ids
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import (
	ActiveSkillStatTarget,
	EggStatTarget,
	MountStatTarget,
)
from core.game_logic.config.summon_config import SummonConfig
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


@miraesee_extension
def resolved_summon_cost(
	player: PlayerModel,
	summon_config: SummonConfig,
	summon_count: int,
) -> int:
	base_amount = summon_config.single_summon_cost.amount * summon_count
	target = summon_config.summonable_id.get_stat_target()
	return StatHelper.calculate_value_round_to_int(
		player,
		StatType.Cost,
		target,
		base_amount,
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


def _run_egg_summon_rolls(
	player: PlayerModel,
	summon_count: int,
) -> tuple[MetaActionResult, list[SummonedEggInfo]]:
	game_config = player.game_config
	summon_config = game_config.egg_summon_config
	collection = player.player_pet_collection_model
	summon_model = collection.summon_model
	summoned: list[SummonedEggInfo] = []

	freebie_target = EggStatTarget()
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
		egg = collection.create_egg_model(rolled_rarity, summon_model.seed)
		is_new = all(existing.rarity != rolled_rarity for existing in collection.eggs)
		collection.eggs.append(egg)
		summoned.append(SummonedEggInfo(egg, is_new))

		summon_model.increment_summon_count(summon_config)
		i += 1

	return ActionResult.Success, summoned


def _run_mount_summon_rolls(
	player: PlayerModel,
	summon_count: int,
) -> tuple[MetaActionResult, list[SummonedMountsInfo]]:
	game_config = player.game_config
	summon_config = game_config.mount_summon_config
	collection = player.player_mount_collection_model
	summon_model = collection.summon_model
	summoned: list[SummonedMountsInfo] = []

	freebie_target = MountStatTarget()
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
		candidates = _mount_ids_for_rarity(game_config.mount_library, rolled_rarity)
		if not candidates:
			return ActionResult.DoesNotExist, summoned

		mount = create_mount_from_ids(player, candidates, rng)
		is_new = all(
			existing.mount_id != mount.mount_id
			for existing in collection.player_mount_models
		)
		collection.player_mount_models.append(mount)
		summoned.append(SummonedMountsInfo(mount, is_new))

		summon_model.increment_summon_count(summon_config)
		i += 1

	return ActionResult.Success, summoned


@miraesee_extension
def egg_summon_allow_overdraft(
	logic: GameLogic,
	summon_count: int,
	*,
	commit: bool = True,
) -> tuple[MetaActionResult, list[SummonedEggInfo]]:
	player = logic.player
	summon_config = player.game_config.egg_summon_config
	currency = summon_config.single_summon_cost.currency

	if summon_count not in summon_config.possible_summon_count:
		return ActionResult.DoesNotExist, []

	cost = resolved_summon_cost(player, summon_config, summon_count)
	if not commit:
		return ActionResult.Success, []

	spend_context = player.player_currency_model.create_spend_context(
		player,
		currency,
		cost,
	)
	spend_context.spend("EggSummon")
	return _run_egg_summon_rolls(player, summon_count)


@miraesee_extension
def mount_summon_allow_overdraft(
	logic: GameLogic,
	summon_count: int,
	*,
	commit: bool = True,
) -> tuple[MetaActionResult, list[SummonedMountsInfo]]:
	player = logic.player
	summon_config = player.game_config.mount_summon_config
	currency = summon_config.single_summon_cost.currency

	if summon_count not in summon_config.possible_summon_count:
		return ActionResult.DoesNotExist, []

	cost = resolved_summon_cost(player, summon_config, summon_count)
	if not commit:
		return ActionResult.Success, []

	spend_context = player.player_currency_model.create_spend_context(
		player,
		currency,
		cost,
	)
	spend_context.spend("MountSummon")
	return _run_mount_summon_rolls(player, summon_count)
