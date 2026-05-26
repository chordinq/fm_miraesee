from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field

from core.game_logic.summon_base import SummonPullResult

KIND_ORDER = ("skill", "egg", "mount")


@dataclass
class SummonHistoryEntry:
    kind: str
    count: int
    pulls: list[SummonPullResult] = field(default_factory=list)
    bonus: int = 0


@dataclass
class SummonHistory:
    entries: list[SummonHistoryEntry] = field(default_factory=list)
    _seq: int = 0

    def add(self, kind: str, count: int, pulls: list[SummonPullResult]) -> None:
        bonus = sum(1 for p in pulls if getattr(p, "is_bonus", False))
        self.entries.append(SummonHistoryEntry(kind=kind, count=count, pulls=list(pulls), bonus=bonus))
        self._seq += 1

    def clear(self) -> None:
        self.entries.clear()
