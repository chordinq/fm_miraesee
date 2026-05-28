# ui/theme/metrics.py — all layout numbers in one place (single source of truth)
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# ---------------------------------------------------------------------------
# Window / Hub chrome
# ---------------------------------------------------------------------------
START_FULLSCREEN = True
WINDOW_MIN_W = 640
WINDOW_MIN_H = 400
WINDOW_DEFAULT_W = 960
WINDOW_DEFAULT_H = 540

TAB_BAR_HEIGHT = 40
GEAR_TAB_WIDTH = 36
FOOTER_HEIGHT = 40
FOOTER_MARGIN_H = 8
FOOTER_MARGIN_V = 4

DUMP_BTN_WIDTH = 120
DUMP_CENTER_SPACING = 12
DUMP_BTN_SPACING = 8

# ---------------------------------------------------------------------------
# Collection grid / panel
# ---------------------------------------------------------------------------
GRID_MARGIN = 8
GRID_GAP = 6
GRID_COLS = 5
COLLECTION_TILE_W = 72
COLLECTION_TILE_H = 88
COLLECTION_ICON_SIZE = 52

SKILL_CIRCLE_SIZE = 56
SKILL_CIRCLE_BORDER = 3
SKILL_TILE_W = 76
SKILL_TILE_H = 96
SKILL_ICON_SIZE = 52

FRAMED_GRID_H_GAP = 4
FRAMED_GRID_V_GAP = 10
FRAMED_GRID_MARGIN_H = 4
FRAMED_TILE_W = SKILL_TILE_W
FRAMED_TILE_H = 80
FRAME_SIZE = SKILL_CIRCLE_SIZE
FRAME_BORDER = 3
FRAME_RADIUS = 10
FRAME_SPRITE_SIZE = SKILL_ICON_SIZE

EGG_TILE_W = FRAMED_TILE_W
EGG_TILE_H = FRAMED_TILE_H
EGG_ICON_SIZE = FRAME_SIZE
EGG_ICON_TOP_MARGIN = 4
TILE_CAPTION_OVERLAP = 10

EQUIPPED_BADGE_PAD_X = 6
EQUIPPED_BADGE_PAD_Y = 1
EQUIPPED_BADGE_BG_ALPHA = 224
SKILL_SHARD_BAR_W = SKILL_TILE_W - 8
SKILL_SHARD_BAR_H = 16
SKILL_SHARD_BAR_BORDER = 2
DETAIL_ICON_FRAME_SIZE = 72
DETAIL_ICON_STACK_W = FRAMED_TILE_W

TILE_SIZE = COLLECTION_TILE_W

COLLECTION_PANEL_PAD_TOP = 10
COLLECTION_PANEL_PAD_LEFT = 14
COLLECTION_PANEL_PAD_RIGHT = 10
COLLECTION_PANEL_PAD_BOTTOM = 6
COLLECTION_GRID_PAD_TOP = 6

SKILL_SUMMON_BAR_HEIGHT = 80
SKILL_SUMMON_REPEAT_OPTIONS = (1, 5, 10, 25)

CURRENCY_STRIP_FONT_SIZE = 15
CURRENCY_STRIP_ICON = 26
CURRENCY_STRIP_ROW_H = 34
CURRENCY_STRIP_CHIP_GAP = 3
PET_SUBHEADER_HEIGHT = 76
EQUIPPED_BAR_HEIGHT = PET_SUBHEADER_HEIGHT
EQUIPPED_BAR_SLOT_ICON = 48
EQUIPPED_BAR_SLOT_W = EQUIPPED_BAR_SLOT_ICON + 4
EQUIPPED_BAR_SLOT_H = EQUIPPED_BAR_SLOT_ICON + 20
EQUIPPED_BAR_SLOT_GAP = 10
EQUIPPED_BAR_RIBBON_W = 88


def pet_collection_content_width() -> int:
    return GRID_COLS * FRAMED_TILE_W + (GRID_COLS - 1) * FRAMED_GRID_H_GAP


def pet_collection_outer_width(margin_h: int = FRAMED_GRID_MARGIN_H) -> int:
    return margin_h * 2 + pet_collection_content_width()


def collection_panel_width(margin_h: int = FRAMED_GRID_MARGIN_H) -> int:
    return (
        pet_collection_outer_width(margin_h)
        + COLLECTION_PANEL_PAD_LEFT
        + COLLECTION_PANEL_PAD_RIGHT
    )


# ---------------------------------------------------------------------------
# Hatch bar
# ---------------------------------------------------------------------------
HATCH_SLOT_COUNT = 4
HATCH_SLOT_GAP = 6

HATCH_SLOT_ORIGIN_X = -0.8
HATCH_SLOT_ORIGIN_Y = -0.09
HATCH_SLOT_REF_W = 6.3
HATCH_SLOT_REF_H = 8.84

HATCH_SCENE_W = FRAMED_TILE_W
HATCH_SCENE_H = max(1, round(HATCH_SCENE_W * HATCH_SLOT_REF_H / HATCH_SLOT_REF_W))
HATCH_BAR_PAD_V = 12
HATCH_BAR_PAD_H = 12
HATCH_SCENE_MIN_W = FRAMED_TILE_W
HATCH_SCENE_MIN_H = max(1, round(HATCH_SCENE_MIN_W * HATCH_SLOT_REF_H / HATCH_SLOT_REF_W))
HATCH_BAR_MIN_HEIGHT = HATCH_SCENE_MIN_H + HATCH_BAR_PAD_V * 2


def hatch_slots_row_width(scene_w: int) -> int:
    return HATCH_SLOT_COUNT * scene_w + (HATCH_SLOT_COUNT - 1) * HATCH_SLOT_GAP


def hatch_bar_content_height(scene_h: int) -> int:
    return scene_h + 2 * HATCH_BAR_PAD_V


def hatch_scene_size_for_panel_width(panel_inner_width: int) -> tuple[int, int]:
    inner_w = max(HATCH_SCENE_MIN_W * HATCH_SLOT_COUNT, panel_inner_width)
    max_scene_w = (inner_w - (HATCH_SLOT_COUNT - 1) * HATCH_SLOT_GAP) // HATCH_SLOT_COUNT
    scene_w = max(HATCH_SCENE_MIN_W, max_scene_w)
    scene_h = max(HATCH_SCENE_MIN_H, round(scene_w * HATCH_SLOT_REF_H / HATCH_SLOT_REF_W))
    return scene_w, scene_h


@dataclass(frozen=True)
class HatchBarMetrics:
    scene_w: int
    scene_h: int
    slot_gap: int
    pad_h: int
    pad_v: int

    @property
    def row_width(self) -> int:
        return hatch_slots_row_width(self.scene_w)

    @property
    def bar_height(self) -> int:
        return hatch_bar_content_height(self.scene_h)


def hatch_bar_content_width(
    panel_width: int,
    *,
    grid_margin_h: int = FRAMED_GRID_MARGIN_H,
) -> int:
    return (
        panel_width
        - COLLECTION_PANEL_PAD_RIGHT
        - COLLECTION_PANEL_PAD_LEFT
        - 2 * grid_margin_h
    )


def hatch_bar_horizontal_margins(
    *,
    grid_margin_h: int = FRAMED_GRID_MARGIN_H,
) -> tuple[int, int]:
    return (
        COLLECTION_PANEL_PAD_RIGHT + grid_margin_h,
        COLLECTION_PANEL_PAD_LEFT + grid_margin_h,
    )


def hatch_bar_metrics(
    panel_width: int,
    *,
    grid_margin_h: int = FRAMED_GRID_MARGIN_H,
) -> HatchBarMetrics:
    content_w = hatch_bar_content_width(panel_width, grid_margin_h=grid_margin_h)
    scene_w, scene_h = hatch_scene_size_for_panel_width(max(1, content_w))
    return HatchBarMetrics(
        scene_w=scene_w,
        scene_h=scene_h,
        slot_gap=HATCH_SLOT_GAP,
        pad_h=0,
        pad_v=HATCH_BAR_PAD_V,
    )


# ---------------------------------------------------------------------------
# Pet summon bar
# ---------------------------------------------------------------------------
PET_SUMMON_BAR_HEIGHT = 108
PET_SUMMON_BAR_PAD_V = 14
PET_SUMMON_BAR_PAD_H = 12
PET_SUMMON_BUTTON_H = 76
PET_SUMMON_BUTTON_MAX_W = 320
PET_SUMMON_BUTTON_MIN_W = 220
PET_SUMMON_BUTTON_COLOR = "#0081CC"
PET_SUMMON_COST_ICON = 20
PET_SUMMON_COST_X = 18
PET_SUMMON_COST_Y = 14
PET_SUMMON_COST_GAP = 5
PET_SUMMON_TITLE_Y_RATIO = 0.42

# ---------------------------------------------------------------------------
# Currency pill
# ---------------------------------------------------------------------------
CURRENCY_PILL_REF_H = 4.0
CURRENCY_PILL_ICON = 4.0
CURRENCY_PILL_BAR_W = 11.0
CURRENCY_PILL_BAR_H = 2.25
CURRENCY_PILL_BAR_RADIUS = 0.58
CURRENCY_PILL_OUTLINE = 0.25
CURRENCY_PILL_BAR_X = 1.5
CURRENCY_PILL_ICON_CENTER_X = 2.0
CURRENCY_PILL_ICON_CENTER_Y = 2.0
CURRENCY_PILL_BAR_FILL = "#606060"
CURRENCY_PILL_OUTLINE_COLOR = "#000000"
CURRENCY_PILL_UNIT_PX = 10
CURRENCY_PILL_TEXT_PAD_RIGHT = 0.35
CURRENCY_PILL_FONT_REF = 1.35


def currency_pill_ref_width() -> float:
    icon_right = CURRENCY_PILL_ICON_CENTER_X + CURRENCY_PILL_ICON / 2.0
    bar_right = CURRENCY_PILL_BAR_X + CURRENCY_PILL_BAR_W
    return max(icon_right, bar_right) + CURRENCY_PILL_OUTLINE


CURRENCY_PILL_REF_W = currency_pill_ref_width()


def currency_pill_pixel_size() -> tuple[int, int]:
    u = CURRENCY_PILL_UNIT_PX
    return round(currency_pill_ref_width() * u), round(CURRENCY_PILL_REF_H * u)


def currency_pill_scale() -> float:
    return float(CURRENCY_PILL_UNIT_PX)


# ---------------------------------------------------------------------------
# Forge
# ---------------------------------------------------------------------------
EQUIP_SLOT_W = 100
EQUIP_SLOT_H = 98
EQUIP_ICON_SIZE = 72
EQUIP_CAPTION_BOTTOM_INSET = 0
EQUIP_SLOT_GAP = 10
EQUIP_GRID_MARGIN = 24

# ---------------------------------------------------------------------------
# Equipped badges
# ---------------------------------------------------------------------------
EquippedBadgeAnchor = Literal["center", "bottom"]


@dataclass(frozen=True)
class EquippedBadgePlacement:
    host_w: int
    host_h: int
    badge_w: int | None = None
    anchor: EquippedBadgeAnchor = "center"
    offset_x: int = 0
    offset_y: int = 0
    bottom_inset: int = 0


def equipped_badge_xy(
    placement: EquippedBadgePlacement,
    badge_w: int,
    badge_h: int,
) -> tuple[int, int]:
    px = placement.offset_x
    py = placement.offset_y
    if badge_w >= placement.host_w:
        x = px
    else:
        x = (placement.host_w - badge_w) // 2 + px
    if placement.anchor == "bottom":
        y = placement.host_h - badge_h - placement.bottom_inset + py
    else:
        y = (placement.host_h - badge_h) // 2 + py
    return max(0, x), max(0, y)


EQUIPPED_BADGE_PET_MOUNT = EquippedBadgePlacement(
    host_w=FRAMED_TILE_W,
    host_h=FRAME_SIZE,
    badge_w=FRAMED_TILE_W,
)
EQUIPPED_BADGE_SKILL = EquippedBadgePlacement(
    host_w=SKILL_TILE_W,
    host_h=SKILL_CIRCLE_SIZE,
    badge_w=SKILL_TILE_W,
)
EQUIPPED_BADGE_DETAIL = EquippedBadgePlacement(
    host_w=DETAIL_ICON_STACK_W,
    host_h=DETAIL_ICON_FRAME_SIZE,
    badge_w=DETAIL_ICON_FRAME_SIZE,
)
