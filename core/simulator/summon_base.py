"""
ONLY FOR REFERENCE — disabled until game_logic APIs are migrated.
Re-enable by uncommenting the block below.
"""

# from __future__ import annotations
#
# from dataclasses import dataclass, field
# from typing import Optional
#
# from core.game_logic.enums import AscendableType, Rarity
# from core.game_logic.secondary_stats import SecondaryStats
#
#
# @dataclass
# class SummonPullResult:
# 	rarity:          Rarity
# 	is_new:          bool
# 	detail:          str
# 	is_bonus:        bool                         = False
# 	secondary_stats: Optional[SecondaryStats] = None
# 	egg_seed:        Optional[int]                = None
# 	pet_idx:         Optional[int]                = None
#
#
# @dataclass
# class SummonResult:
# 	ascendable_type: AscendableType
# 	requested_count: int
# 	actual_count:    int
# 	pulls:           list[SummonPullResult] = field(default_factory=list)
# 	success:         bool                  = True
# 	error:           str | None            = None
