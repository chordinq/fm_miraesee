# core/game_logic/GameLogic.py
"""
GameLogic -- public API facade.

The game engine's top-level object. Owns a PlayerModel and exposes
simulation actions as methods. Delegates all logic to the individual
modules in core/game_logic/.
"""

from __future__ import annotations

from configs import SKILL_SUMMON_CONFIG, EGG_SUMMON_CONFIG, MOUNT_SUMMON_CONFIG
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.forge import ForgeResult, ForgeSimulator
from core.game_logic.skill_summon import SkillSummonSimulator
from core.game_logic.egg_summon import EggSummonSimulator
from core.game_logic.mount_summon import MountSummonSimulator
from core.game_logic.summon_base import SummonResult


class GameLogic:
	"""
	Entry point for all game simulations.

	Usage::

	    gl = GameLogic(player)
	    result = gl.forge(20)
	    result = gl.summon_skills(5)
	    result = gl.summon_eggs(1)
	    result = gl.summon_mounts(1)
	"""

	def __init__(self, player: PlayerModel) -> None:
		self._player = player

	@property
	def player(self) -> PlayerModel:
		return self._player

	# ------------------------------------------------------------------
	# Forge
	# ------------------------------------------------------------------

	def forge(self, hammer_count: int) -> ForgeResult:
		return ForgeSimulator(self._player).forge(hammer_count)

	# ------------------------------------------------------------------
	# Skill summon
	# ------------------------------------------------------------------

	def summon_skills(self, count: int) -> SummonResult:
		return SkillSummonSimulator(self._player, SKILL_SUMMON_CONFIG).summon(count)

	# ------------------------------------------------------------------
	# Egg (pet) summon
	# ------------------------------------------------------------------

	def summon_eggs(self, count: int) -> SummonResult:
		return EggSummonSimulator(self._player, EGG_SUMMON_CONFIG).summon(count)

	# ------------------------------------------------------------------
	# Mount summon
	# ------------------------------------------------------------------

	def summon_mounts(self, count: int) -> SummonResult:
		return MountSummonSimulator(self._player, MOUNT_SUMMON_CONFIG).summon(count)
