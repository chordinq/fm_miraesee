from __future__ import annotations

from typing import TYPE_CHECKING

from core_test.summon_simulator import (
	egg_summon_allow_overdraft,
	mount_summon_allow_overdraft,
	skill_summon_allow_overdraft,
)
from ui_settings import allow_negative_currency_enabled

if TYPE_CHECKING:
	from core.game_logic.game_logic import GameLogic
	from core.game_logic.summon_config import SummonConfig


def can_afford_summon_for_ui(
	summon_config: SummonConfig,
	player,
	count: int,
) -> bool:
	if count not in summon_config.possible_summon_count:
		return False
	if allow_negative_currency_enabled():
		return True
	can_afford, _ = summon_config.can_afford_summon(player, count)
	return can_afford


def execute_skill_summon(logic: GameLogic, count: int, *, commit: bool = True):
	if allow_negative_currency_enabled():
		result, summoned, _ = skill_summon_allow_overdraft(
			logic,
			count,
			commit=commit,
		)
		return result, summoned
	return logic.skill_summon(count, commit=commit)


def execute_egg_summon(logic: GameLogic, count: int, *, commit: bool = True):
	if allow_negative_currency_enabled():
		return egg_summon_allow_overdraft(logic, count, commit=commit)
	return logic.egg_summon(count, commit=commit)


def execute_mount_summon(logic: GameLogic, count: int, *, commit: bool = True):
	if allow_negative_currency_enabled():
		return mount_summon_allow_overdraft(logic, count, commit=commit)
	return logic.mount_summon(count, commit=commit)
