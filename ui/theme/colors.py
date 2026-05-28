# ui/theme/colors.py — palette tokens (single source of truth)
from __future__ import annotations

BG = "#101214"
BG_PANEL = "#1a1e24"
COLLECTION_BG = "#E0E0E0"
COLLECTION_SUBHEADER_BG = COLLECTION_BG
HATCH_BAR_BG = "#465069"
HATCH_READY = "#3dcc5a"
FG = "#e0e0e0"
FG_MUTED = "#8a8a8a"
TAB_ACTIVE = "#ffffff"
TAB_BORDER = "#3a3a3a"
ACCENT = "#4a7eb8"
ACCENT_HOVER = "#5a8ec8"
BTN_MUTED = "#2a2a2e"
TILE_PLACEHOLDER = "#2a3040"

DOMAIN_COLORS: dict[str, str] = {
    "profile": "#e0e0e0",
    "forge": "#c2c2c2",
    "skill": "#8afa4f",
    "pet": "#6394c9",
    "mount": "#f0e762",
    "techtree": "#dd565b",
}

AGE_COLORS: dict[int, str] = {
    0: "#F1F1F1",
    1: "#5DD8FF",
    2: "#5DFF8A",
    3: "#FCFF5D",
    4: "#FF5D5D",
    5: "#D55DFF",
    6: "#75FFEE",
    7: "#7D5DFF",
    8: "#B07879",
    9: "#FF9E0D",
}

RARITY_COLORS: dict[int, str] = {
    0: AGE_COLORS[0],
    1: AGE_COLORS[1],
    2: AGE_COLORS[2],
    3: AGE_COLORS[3],
    4: AGE_COLORS[4],
    5: AGE_COLORS[5],
}

AGE_BORDER: dict[int, str] = dict(AGE_COLORS)
RARITY_BORDER: dict[int, str] = dict(RARITY_COLORS)
RARITY_FRAME: dict[int, str] = dict(RARITY_COLORS)
