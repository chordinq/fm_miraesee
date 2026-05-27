# ui/constants/colors.py — palette tokens (aligned with in-game age / rarity CSS)
from __future__ import annotations

BG = "#101214"
BG_PANEL = "#1a1e24"
COLLECTION_BG = "#E0E0E0"
HATCH_BAR_BG = "#0c121c"
HATCH_READY = "#3dcc5a"
FG = "#e0e0e0"
FG_MUTED = "#8a8a8a"
TAB_ACTIVE = "#ffffff"
TAB_BORDER = "#3a3a3a"
ACCENT = "#4a7eb8"
ACCENT_HOVER = "#5a8ec8"
BTN_MUTED = "#2a2a2e"
TILE_PLACEHOLDER = "#2a3040"

# Hub tab accent (domain key → label / active underline)
DOMAIN_COLORS: dict[str, str] = {
    "profile": "#e0e0e0",
    "forge": "#c2c2c2",
    "skill": "#8afa4f",
    "pet": "#6394c9",
    "mount": "#f0e762",
    "techtree": "#dd565b",
}

# ItemAge (ItemAge enum 0..9) — --age-* / --color-*-rgb
AGE_COLORS: dict[int, str] = {
    0: "#F1F1F1",  # Primitive
    1: "#5DD8FF",  # Medieval
    2: "#5DFF8A",  # Early Modern
    3: "#FCFF5D",  # Modern
    4: "#FF5D5D",  # Space
    5: "#D55DFF",  # Interstellar
    6: "#75FFEE",  # Multiverse
    7: "#7D5DFF",  # Quantum
    8: "#B07879",  # Underworld
    9: "#FF9E0D",  # Divine
}

# Rarity (Rarity enum 0..5) — maps to age palette via --rarity-*
RARITY_COLORS: dict[int, str] = {
    0: AGE_COLORS[0],  # Common → Primitive
    1: AGE_COLORS[1],  # Rare → Medieval
    2: AGE_COLORS[2],  # Epic → Early Modern
    3: AGE_COLORS[3],  # Legendary → Modern
    4: AGE_COLORS[4],  # Ultimate → Space
    5: AGE_COLORS[5],  # Mythic → Interstellar
}

# Forge equipment slot borders (ItemAge)
AGE_BORDER: dict[int, str] = dict(AGE_COLORS)

# Collection tile borders (skill eggs use Rarity)
RARITY_BORDER: dict[int, str] = dict(RARITY_COLORS)

# Pet / mount rounded frame fill (same in-game rarity tint)
RARITY_FRAME: dict[int, str] = dict(RARITY_COLORS)
