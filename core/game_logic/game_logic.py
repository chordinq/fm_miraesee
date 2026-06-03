"""
GameLogic entry point — simulator actions disabled (see core/simulator/).
"""
from __future__ import annotations

from .models.player_model import PlayerModel
from .summon_config import (
	EGG_SUMMON_CONFIG,
	MOUNT_SUMMON_CONFIG,
	SKILL_SUMMON_CONFIG,
)

# ONLY FOR REFERENCE — simulators commented out under core/simulator/
# from core.simulator import (
# 	EggSummonSimulator,
# 	ForgeResult,
# 	ForgeSimulator,
# 	MountSummonSimulator,
# 	SkillSummonSimulator,
# 	SummonResult,
# )


class GameLogic:
	def __init__(self, player: PlayerModel) -> None:
		self._player = player

	@property
	def player(self) -> PlayerModel:
		return self._player

	# def ForgeAction(self, hammer_count: int) -> ForgeResult:
	# 	return ForgeSimulator(self._player).forge(hammer_count)
	#
	# def SkillSummonAction(self, count: int) -> SummonResult:
	# 	return SkillSummonSimulator(self._player, SKILL_SUMMON_CONFIG).summon(count)
	#
	# def EggSummonAction(self, count: int) -> SummonResult:
	# 	return EggSummonSimulator(self._player, EGG_SUMMON_CONFIG).summon(count)
	#
	# def MountSummonAction(self, count: int) -> SummonResult:
	# 	return MountSummonSimulator(self._player, MOUNT_SUMMON_CONFIG).summon(count)
