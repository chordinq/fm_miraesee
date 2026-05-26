# cli/store/models.py
"""Data models for the summon-result store."""

from __future__ import annotations
from dataclasses import dataclass, field

RARITY_ORDER: dict[str, int] = {
    "Common": 0, "Rare": 1, "Epic": 2,
    "Legendary": 3, "Ultimate": 4, "Mythic": 5,
}


@dataclass
class SummonRecord:
    id:               int   = 0
    session_id:       str   = ""
    dump_hash:        str   = ""
    kind:             str   = ""    # "skill" | "egg" | "mount"
    batch_ts:         str   = ""    # ISO 8601 UTC
    pull_global_idx:  int   = 0     # ever-increasing per session
    pull_batch_idx:   int   = 0     # 0-based index within this batch
    rarity:           str   = ""
    name:             str   = ""
    is_bonus:         bool  = False
    stat1_type:       str   | None = None
    stat1_perf:       float | None = None   # 0-100
    stat1_val:        float | None = None   # in-game %
    stat2_type:       str   | None = None
    stat2_perf:       float | None = None
    stat2_val:        float | None = None
    egg_seed:         int   | None = None
    pet_idx:          int   | None = None
    pet_type:         str   | None = None   # "Damage"|"Health"|"Balanced"

    @property
    def rarity_value(self) -> int:
        return RARITY_ORDER.get(self.rarity, 0)


@dataclass
class SummonFilter:
    """SQL-like filter for querying the summon store."""
    kind:             str        | None = None
    session_id:       str        | None = None
    min_rarity:       str        | None = None   # "Rare" → Rare+
    stat_types:       list[str]         = field(default_factory=list)     # ALL must be present
    any_stat_types:   list[str]         = field(default_factory=list)     # ANY must be present
    min_perf:         float      | None = None   # 0-100
    max_perf:         float      | None = None
    min_val:          float      | None = None   # in-game %
    max_val:          float      | None = None
    pet_type:         str        | None = None
    is_bonus:         bool       | None = None
    name_contains:    str        | None = None
    limit:            int               = 100
    offset:           int               = 0
    order_by:         str               = "id DESC"
