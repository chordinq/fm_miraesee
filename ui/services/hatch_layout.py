# ui/services/hatch_layout.py — hatch slot layout from in-game proportions (PPT reference)
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtGui import QPixmap

from core.game_logic.player_model.EggModel import EggModel
from ui.constants.layout import EGG_ICON_SIZE, HATCH_SCENE_H, HATCH_SCENE_W
from ui.services.hatch_sprites import (
    center_pixmap,
    hatch_bed_pixmap,
    hatch_cone_pixmap,
    hatch_lamp_pixmap,
)
from ui.services.sheet_sprites import egg_icon_pixmap

# PowerPoint reference frame (relative units; top-left origin per layer)
_REF_SCENE_W = 4.15
_REF_SCENE_H = 5.9

# (left, top, width, height)
_SPEC_LAMP = (1.05, 0.0, 2.0, 2.0)
_SPEC_CONE = (0.0, 0.47, 4.15, 4.15)
_SPEC_BED = (0.29, 2.23, 3.6, 3.6)
_SPEC_EGG = (1.07, 2.55, 2.0, 2.0)


@dataclass(frozen=True)
class HatchLayer:
    pixmap: QPixmap
    x: int
    y: int


def _scale_xy() -> tuple[float, float]:
    return HATCH_SCENE_W / _REF_SCENE_W, HATCH_SCENE_H / _REF_SCENE_H


def _rel_to_pixel(left: float, top: float, width: float, height: float) -> tuple[int, int, int, int]:
    sx, sy = _scale_xy()
    return (
        round(left * sx),
        round(top * sy),
        max(1, round(width * sx)),
        max(1, round(height * sy)),
    )


def _rel_center_to_topleft(cx: float, cy: float, width: int, height: int) -> tuple[int, int]:
    sx, sy = _scale_xy()
    return round(cx * sx - width / 2), round(cy * sy - height / 2)


def _layer_at(
    loader,
    spec: tuple[float, float, float, float],
) -> HatchLayer | None:
    x, y, pw, ph = _rel_to_pixel(*spec)
    pix = loader(pw, ph)
    if pix is None or pix.isNull():
        return None
    return HatchLayer(pix, x, y)


def build_hatch_layers(egg: EggModel | None) -> list[HatchLayer]:
    """
    Paint order back → front: bed → cone → lamp → egg.
    List order matches QWidget child stacking (first = back).
    """
    active = egg is not None
    layers: list[HatchLayer] = []

    bed = _layer_at(lambda w, h: hatch_bed_pixmap(w, h), _SPEC_BED)
    if bed is not None:
        layers.append(bed)

    if active:
        cone = _layer_at(lambda w, h: hatch_cone_pixmap(w, h), _SPEC_CONE)
        if cone is not None:
            layers.append(cone)

    lamp = _layer_at(lambda w, h: hatch_lamp_pixmap(active, w, h), _SPEC_LAMP)
    if lamp is not None:
        layers.append(lamp)

    if active and egg is not None:
        egg_cx = _SPEC_EGG[0] + _SPEC_EGG[2] / 2
        egg_cy = _SPEC_EGG[1] + _SPEC_EGG[3] / 2
        ex, ey = _rel_center_to_topleft(egg_cx, egg_cy, EGG_ICON_SIZE, EGG_ICON_SIZE)
        egg_raw = egg_icon_pixmap(egg, EGG_ICON_SIZE)
        egg_pix = center_pixmap(egg_raw, EGG_ICON_SIZE, EGG_ICON_SIZE)
        if egg_pix is not None and not egg_pix.isNull():
            layers.append(HatchLayer(egg_pix, ex, ey))

    return layers
