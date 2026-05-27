# ui/constants/layout.py — section sizes, spacing, window defaults
from __future__ import annotations

# Window
START_FULLSCREEN = True
WINDOW_MIN_W = 640
WINDOW_MIN_H = 400
WINDOW_DEFAULT_W = 960
WINDOW_DEFAULT_H = 540

# Hub chrome
TAB_BAR_HEIGHT = 40
GEAR_TAB_WIDTH = 36
FOOTER_HEIGHT = 40
FOOTER_MARGIN_H = 8
FOOTER_MARGIN_V = 4

# Forge equipment panel
EQUIP_SLOT_W = 100
EQUIP_SLOT_H = 118
EQUIP_ICON_SIZE = 72
EQUIP_SLOT_GAP = 10
EQUIP_GRID_MARGIN = 24

# Collection grid (skill / eggs)
GRID_MARGIN = 8
GRID_GAP = 6
GRID_COLS = 5
COLLECTION_TILE_W = 72
COLLECTION_TILE_H = 88
COLLECTION_ICON_SIZE = 52

# Skill — circular rarity disk
SKILL_CIRCLE_SIZE = 56
SKILL_CIRCLE_BORDER = 3
SKILL_TILE_W = 76
SKILL_TILE_H = 96
SKILL_ICON_SIZE = 52

# Pet / mount framed grid (match skill tile footprint)
FRAMED_GRID_H_GAP = 4
FRAMED_GRID_V_GAP = 10
FRAMED_GRID_MARGIN_H = 4
FRAMED_TILE_W = SKILL_TILE_W
FRAMED_TILE_H = 80
FRAME_SIZE = SKILL_CIRCLE_SIZE
FRAME_BORDER = 3
FRAME_RADIUS = 10
FRAME_SPRITE_SIZE = SKILL_ICON_SIZE

# Eggs in pet grid — same icon band as pet frame
EGG_TILE_W = FRAMED_TILE_W
EGG_TILE_H = FRAMED_TILE_H
EGG_ICON_SIZE = FRAME_SIZE
EGG_ICON_TOP_MARGIN = 4

TILE_SIZE = COLLECTION_TILE_W  # legacy placeholder tiles

# Collection panel (skill / pet / mount) — gray band inset from hub edges
COLLECTION_PANEL_PAD_TOP = 10
COLLECTION_PANEL_PAD_LEFT = 14
COLLECTION_PANEL_PAD_RIGHT = 10
COLLECTION_PANEL_PAD_BOTTOM = 6
COLLECTION_GRID_PAD_TOP = 6

# Pet collection + hatch (shared 5-column band)
def pet_collection_content_width() -> int:
    """Width of the 5-column tile band (no side margins)."""
    return GRID_COLS * FRAMED_TILE_W + (GRID_COLS - 1) * FRAMED_GRID_H_GAP


def pet_collection_outer_width(margin_h: int = FRAMED_GRID_MARGIN_H) -> int:
    return margin_h * 2 + pet_collection_content_width()


def collection_panel_width(margin_h: int = FRAMED_GRID_MARGIN_H) -> int:
    return (
        pet_collection_outer_width(margin_h)
        + COLLECTION_PANEL_PAD_LEFT
        + COLLECTION_PANEL_PAD_RIGHT
    )


# Hatch: 4 slots centered in the same content width; egg matches EGG_ICON_SIZE
HATCH_SLOT_COUNT = 4
HATCH_SLOT_GAP = FRAMED_GRID_H_GAP
_HATCH_REF_ASPECT = 5.9 / 4.15
HATCH_SCENE_W = (
    pet_collection_content_width() - (HATCH_SLOT_COUNT - 1) * HATCH_SLOT_GAP
) // HATCH_SLOT_COUNT
HATCH_SCENE_H = round(HATCH_SCENE_W * _HATCH_REF_ASPECT)
HATCH_BAR_HEIGHT = HATCH_SCENE_H + 8

# Dump screen
DUMP_BTN_WIDTH = 120
DUMP_CENTER_SPACING = 12
DUMP_BTN_SPACING = 8
