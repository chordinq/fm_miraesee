# core/game_logic/stat_helper/StatHelper.py
"""
Game.Logic.StatHelper

Utility for stat-based rolls used during summon bonus checks.
All methods are static; no instance state needed.
"""

from __future__ import annotations

from core.enums import TechTreeNodeType, SummonKind
from core.random_pcg import RandomPCG, U32_DENOM

_EXTRA_SUMMON_MAX_RESEARCH   = 25
_EXTRA_SUMMON_PCT_PER_LEVEL  = 2.0   # Egg / Mount: +2 % per level, cap 50 %
_SKILL_BONUS_PCT_PER_LEVEL   = 0.5   # Skill: +0.5 % per level, cap 100 %


class StatHelper:
	"""
	Game.Logic.StatHelper -- static utility class.

	Maps C# StatHelper$$RollStat and related helpers.
	"""

	@staticmethod
	def extra_summon_threshold(player, kind: SummonKind) -> int:
		"""
		Compute the raw uint32 threshold used in the bonus extra-summon roll.

		  Egg / Mount: TechTree node x 2 %, capped at 25 levels (50 %)
		  Skill:       GhostTownSkillBonus x 0.5 %, capped at 100 %

		Returns a uint32 value; compare with rng._next_pcg32() < threshold.
		"""
		if kind == SummonKind.Pets:
			node  = TechTreeNodeType.ExtraEggChance
			level = min(_EXTRA_SUMMON_MAX_RESEARCH, player.get_tech_level(node))
			pct   = level * _EXTRA_SUMMON_PCT_PER_LEVEL
		elif kind == SummonKind.Mounts:
			node  = TechTreeNodeType.ExtraMountChance
			level = min(_EXTRA_SUMMON_MAX_RESEARCH, player.get_tech_level(node))
			pct   = level * _EXTRA_SUMMON_PCT_PER_LEVEL
		else:  # Skills
			node  = TechTreeNodeType.GhostTownSkillBonus
			level = player.get_tech_level(node)
			pct   = min(100.0, level * _SKILL_BONUS_PCT_PER_LEVEL)

		return int(round((pct / 100.0) * U32_DENOM))

	@staticmethod
	def roll_bonus_summon(player, kind: SummonKind, rng: RandomPCG) -> bool:
		"""
		StatHelper$$RollStat(player, AttackSpeed, target, rng)

		Always consumes exactly 1 PCG call (NextFixedD6 equivalent),
		even when the bonus chance is 0 % (e.g. skill summons with no tech researched).
		Returns True if a bonus pull should be added.
		"""
		threshold = StatHelper.extra_summon_threshold(player, kind)
		roll = rng._next_pcg32()
		if threshold <= 0:
			return False
		return roll < threshold
