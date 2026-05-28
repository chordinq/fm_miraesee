# ui/services/hatch_layout.py — hatch slot layout (PowerPoint reference, top-left origin)
from __future__ import annotations

from dataclasses import dataclass
from functools import partial
from typing import Callable

from PySide6.QtGui import QPixmap

from core.game_logic.player_model.EggModel import EggModel
from ui.theme.metrics import EGG_ICON_SIZE
from ui.theme.metrics import (
    HATCH_SCENE_H,
    HATCH_SCENE_W,
    HATCH_SLOT_ORIGIN_X,
    HATCH_SLOT_ORIGIN_Y,
    HATCH_SLOT_REF_H,
    HATCH_SLOT_REF_W,
)
from ui.services.hatch_sprites import (
    center_pixmap,
    hatch_bed_pixmap,
    hatch_cone_pixmap,
    hatch_lamp_pixmap,
)
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.services.sheet_sprites import egg_icon_pixmap

# PowerPoint slide coords (top-left of each PNG). HatchLight = HatchLampCone.png
# (left, top, width, height)
_SPEC_LAMP = (0.85, -0.09, 3.0, 3.0)
_SPEC_CONE = (-0.8, 0.62, 6.3, 6.3)
_SPEC_BED = (-0.44, 3.15, 5.6, 5.6)
_SPEC_EGG = (0.85, 3.75, 3.0, 3.0)

LayerLoader = Callable[..., QPixmap | None]


@dataclass(frozen=True)
class HatchLayer:
    pixmap: QPixmap
    x: int
    y: int


def _scale_xy(scene_w: int, scene_h: int) -> tuple[float, float]:
    return scene_w / HATCH_SLOT_REF_W, scene_h / HATCH_SLOT_REF_H


def _ppt_to_pixel(
    left: float,
    top: float,
    width: float,
    height: float,
    *,
    scene_w: int,
    scene_h: int,
) -> tuple[int, int, int, int]:
    """Map PPT (hor, ver) to widget pixels; scene origin = normalized top-left."""
    sx, sy = _scale_xy(scene_w, scene_h)
    norm_left = left - HATCH_SLOT_ORIGIN_X
    norm_top = top - HATCH_SLOT_ORIGIN_Y
    return (
        round(norm_left * sx),
        round(norm_top * sy),
        max(1, round(width * sx)),
        max(1, round(height * sy)),
    )


def _layer_at(
    loader: LayerLoader,
    spec: tuple[float, float, float, float],
    *,
    scene_w: int,
    scene_h: int,
    device_pixel_ratio: float,
) -> HatchLayer | None:
    x, y, pw, ph = _ppt_to_pixel(*spec, scene_w=scene_w, scene_h=scene_h)
    pix = loader(pw, ph, device_pixel_ratio=device_pixel_ratio)
    if pix is None or pix.isNull():
        return None
    return HatchLayer(pix, x, y)


def _egg_layer(
    egg: EggModel,
    *,
    scene_w: int,
    scene_h: int,
    device_pixel_ratio: float,
) -> HatchLayer | None:
    """Same icon size as collection grid eggs; centered on the PPT egg anchor."""
    ex, ey, ew, eh = _ppt_to_pixel(*_SPEC_EGG, scene_w=scene_w, scene_h=scene_h)
    egg_sz = EGG_ICON_SIZE
    cx = ex + ew // 2
    cy = ey + eh // 2
    px = cx - egg_sz // 2
    py = cy - egg_sz // 2
    egg_raw = egg_icon_pixmap(
        egg,
        egg_sz,
        device_pixel_ratio=device_pixel_ratio,
    )
    egg_pix = center_pixmap(
        egg_raw,
        egg_sz,
        egg_sz,
        device_pixel_ratio=device_pixel_ratio,
    )
    if egg_pix is None or egg_pix.isNull():
        return None
    return HatchLayer(egg_pix, px, py)


def build_hatch_layers(
    egg: EggModel | None,
    *,
    scene_w: int = HATCH_SCENE_W,
    scene_h: int = HATCH_SCENE_H,
    device_pixel_ratio: float | None = None,
) -> list[HatchLayer]:
    """
    Paint order back → front: bed → cone → lamp → egg.
    List order matches QWidget child stacking (first = back).
    """
    dpr = device_pixel_ratio if device_pixel_ratio is not None else default_device_pixel_ratio()
    active = egg is not None
    layers: list[HatchLayer] = []
    sw, sh = scene_w, scene_h

    bed = _layer_at(
        hatch_bed_pixmap,
        _SPEC_BED,
        scene_w=sw,
        scene_h=sh,
        device_pixel_ratio=dpr,
    )
    if bed is not None:
        layers.append(bed)

    if active:
        cone = _layer_at(
            hatch_cone_pixmap,
            _SPEC_CONE,
            scene_w=sw,
            scene_h=sh,
            device_pixel_ratio=dpr,
        )
        if cone is not None:
            layers.append(cone)

    lamp = _layer_at(
        partial(hatch_lamp_pixmap, active),
        _SPEC_LAMP,
        scene_w=sw,
        scene_h=sh,
        device_pixel_ratio=dpr,
    )
    if lamp is not None:
        layers.append(lamp)

    if active and egg is not None:
        egg_layer = _egg_layer(egg, scene_w=sw, scene_h=sh, device_pixel_ratio=dpr)
        if egg_layer is not None:
            layers.append(egg_layer)

    return layers
