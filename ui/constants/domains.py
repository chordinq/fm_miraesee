# ui/constants/domains.py — hub tab keys (left-to-right order) + localization ids
from __future__ import annotations

# Tab order (domain key)
DOMAINS: tuple[str, ...] = (
    "profile",
    "forge",
    "skill",
    "pet",
    "mount",
    "techtree",
)

# string_tables_en_ko_ja.json entry id per tab (canonical in-game labels)
DOMAIN_TAB_LOC_IDS: dict[str, int] = {
    "profile": 25736002664067072,
    "forge": 280343846912,
    "skill": 2109395617640448,
    "pet": 1762375497347072,
    "mount": 990866679984128,
    "techtree": 4701483102211,
}
