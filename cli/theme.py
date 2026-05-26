# cli/theme.py
"""
Visual theme: ANSI colours + box-drawing constants.

All ANSI sequences are plain strings so they work in any terminal
that understands VT100 escape codes (Windows Terminal, VS Code, etc.).
"""

import sys

# ── ANSI helpers ─────────────────────────────────────────────────────────────

from constants.colors import RESET
BOLD   = "\033[1m"
DIM    = "\033[2m"
ITALIC = "\033[3m"

def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"

def bg_rgb(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"

# ── Palette ───────────────────────────────────────────────────────────────────

C_WHITE   = rgb(255, 255, 255)
C_MUTED   = rgb(160, 160, 160)
C_DIM     = rgb(100, 100, 100)

C_BLUE    = rgb(52,  152, 219)   # info
C_SKY     = rgb(56,  189, 248)   # menu focus (bright sky)
C_GREEN   = rgb(46,  204, 113)   # success / new
C_YELLOW  = rgb(241, 196,  15)   # warning
C_RED     = rgb(231,  76,  60)   # error
C_ORANGE  = rgb(230, 126,  34)   # highlight / bonus

C_GOLD    = rgb(255, 215,   0)   # accent

# Rarity colours (index = Rarity.value)
RARITY_COLORS = [
    rgb(200, 200, 200),   # 0 Common    – light grey
    rgb( 93, 216, 255),   # 1 Rare      – sky blue
    rgb( 93, 255, 138),   # 2 Epic      – green
    rgb(252, 255,  93),   # 3 Legendary – yellow
    rgb(255,  93,  93),   # 4 Ultimate  – red
    rgb(213,  93, 255),   # 5 Mythic    – purple
]

RARITY_NAMES_EN = ["Common", "Rare", "Epic", "Legendary", "Ultimate", "Mythic"]

def age_color(age_value: int) -> str:
    from constants.colors import AGE_COLORS
    return AGE_COLORS.get(age_value, "")


def rarity_color(rarity_value: int) -> str:
    idx = max(0, min(rarity_value, len(RARITY_COLORS) - 1))
    return RARITY_COLORS[idx]

def rarity_str(rarity_value: int) -> str:
    name = RARITY_NAMES_EN[max(0, min(rarity_value, len(RARITY_NAMES_EN) - 1))]
    return f"{rarity_color(rarity_value)}{name}{RESET}"

# Perfection gradient: red → orange → yellow → green (vivid)
_PERF_STOPS: list[tuple[float, tuple[int, int, int]]] = [
    (0.00, (255,  55,  55)),
    (0.33, (255, 140,   0)),
    (0.66, (255, 235,   0)),
    (1.00, ( 60, 255,  80)),
]

def perf_color(perf_pct: float) -> str:
    """perf_pct: 0.0 – 100.0  →  ANSI colour code."""
    t = max(0.0, min(perf_pct / 100.0, 1.0))
    # Find the two stops surrounding t
    for i in range(len(_PERF_STOPS) - 1):
        t0, c0 = _PERF_STOPS[i]
        t1, c1 = _PERF_STOPS[i + 1]
        if t <= t1 or i == len(_PERF_STOPS) - 2:
            span = t1 - t0
            u    = (t - t0) / span if span > 0 else 0.0
            u    = max(0.0, min(u, 1.0))
            r    = int(c0[0] + (c1[0] - c0[0]) * u)
            g    = int(c0[1] + (c1[1] - c0[1]) * u)
            b    = int(c0[2] + (c1[2] - c0[2]) * u)
            return rgb(r, g, b)
    return rgb(*_PERF_STOPS[-1][1])

def colored_perf(perf_pct: float) -> str:
    return f"{perf_color(perf_pct)}{perf_pct:5.1f}%{RESET}"

# ── prompt_toolkit style dict ─────────────────────────────────────────────────

PT_STYLE = {
    "prompt":      "bold #5d8fff",
    "placeholder": "#555555",
}

# ── Box-drawing characters ────────────────────────────────────────────────────

class Box:
    TL = "╭";  TM = "┬";  TR = "╮"
    ML = "├";  MM = "┼";  MR = "┤"
    BL = "╰";  BM = "┴";  BR = "╯"
    H  = "─";  V  = "│"

# Currency colours (defined in constants/colors.py)
from constants.colors import CURRENCY_COLORS  # noqa: F401 — re-export

# ── Misc helpers ──────────────────────────────────────────────────────────────

def ok(msg: str)   -> str: return f"{C_GREEN}{msg}{RESET}"
def warn(msg: str) -> str: return f"{C_YELLOW}{msg}{RESET}"
def err(msg: str)  -> str: return f"{C_RED}{msg}{RESET}"
def info(msg: str) -> str: return f"{C_BLUE}{msg}{RESET}"
def dim(msg: str)  -> str: return f"{DIM}{msg}{RESET}"
def bold(msg: str) -> str: return f"{BOLD}{msg}{RESET}"
