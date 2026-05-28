# ui/theme/config/domains.py — hub tab keys + localization ids
from __future__ import annotations

from core.enums import SummonKind

DOMAINS: tuple[str, ...] = (
    "profile",
    "forge",
    "skill",
    "pet",
    "mount",
    "techtree",
)

DOMAIN_SUMMON_KIND: dict[str, SummonKind] = {
    "skill": SummonKind.Skills,
    "pet": SummonKind.Pets,
    "mount": SummonKind.Mounts,
}

DOMAIN_TAB_LOC_IDS: dict[str, int] = {
    "profile": 25736002664067072,
    "forge": 280343846912,
    "techtree": 4701483102211,
}
