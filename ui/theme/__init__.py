# ui/theme — single source of truth for colors, fonts, metrics, stylesheet, builders, config
from ui.theme.colors import (
    ACCENT,
    ACCENT_HOVER,
    BG,
    BG_PANEL,
    BTN_MUTED,
    FG,
    FG_MUTED,
    TAB_ACTIVE,
    TAB_BORDER,
)
from ui.theme.config.domains import DOMAINS
from ui.theme.metrics import (
    DUMP_BTN_WIDTH,
    FOOTER_HEIGHT,
    GEAR_TAB_WIDTH,
    GRID_COLS,
    GRID_GAP,
    GRID_MARGIN,
    TAB_BAR_HEIGHT,
    TILE_SIZE,
    WINDOW_DEFAULT_H,
    WINDOW_DEFAULT_W,
    WINDOW_MIN_H,
    WINDOW_MIN_W,
)
from ui.theme.stylesheet import global_stylesheet

__all__ = [
    "ACCENT",
    "ACCENT_HOVER",
    "BG",
    "BG_PANEL",
    "BTN_MUTED",
    "DOMAINS",
    "DUMP_BTN_WIDTH",
    "FG",
    "FG_MUTED",
    "FOOTER_HEIGHT",
    "GEAR_TAB_WIDTH",
    "GRID_COLS",
    "GRID_GAP",
    "GRID_MARGIN",
    "TAB_ACTIVE",
    "TAB_BAR_HEIGHT",
    "TAB_BORDER",
    "TILE_SIZE",
    "WINDOW_DEFAULT_H",
    "WINDOW_DEFAULT_W",
    "WINDOW_MIN_H",
    "WINDOW_MIN_W",
    "global_stylesheet",
]
