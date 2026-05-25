# core/game_logic/summon_base.py
"""
Shared dataclasses for all summon simulators.

SummonConfig handles currency checks and spending; these helpers only
carry result data between the simulator and its callers.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from core.enums import Rarity, SummonKind
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel


@dataclass
class SummonPullResult:
	rarity:          Rarity
	is_new:          bool
	detail:          str
	is_bonus:        bool                         = False
	secondary_stats: Optional[SecondaryStatsModel] = None


@dataclass
class SummonResult:
	summon_kind:     SummonKind
	requested_count: int
	actual_count:    int
	pulls:           list[SummonPullResult] = field(default_factory=list)
	success:         bool                  = True
	error:           str | None            = None
