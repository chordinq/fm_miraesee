# ui/services/button0_texture.py — Button_0: 4×2 nine_slice → tint → fit to UI size
from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui.services.nine_slice import DEFAULT_SLICE_MARGIN, nine_slice
from ui.services.pixmap_color import multiply_color
from ui.services.sheet_sprites import texture_path

BUTTON_0_FILE = "Button_0.png"
BUTTON_0_SOURCE_SIZE = 512
BUTTON_0_WIDTH_SCALE = 4
BUTTON_0_HEIGHT_SCALE = 2
BUTTON_0_MASTER_W = BUTTON_0_SOURCE_SIZE * BUTTON_0_WIDTH_SCALE  # 2048
BUTTON_0_MASTER_H = BUTTON_0_SOURCE_SIZE * BUTTON_0_HEIGHT_SCALE  # 1024
BUTTON_0_COLOR = "#0081CC"


@lru_cache(maxsize=1)
def button0_source() -> QPixmap | None:
    path = texture_path(BUTTON_0_FILE)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return None if pix.isNull() else pix


@lru_cache(maxsize=8)
def button0_master(color: str = BUTTON_0_COLOR) -> QPixmap | None:
    """512→2048×1024 (4×2) nine_slice, then multiply tint. Preserves shadow proportions."""
    base = button0_source()
    if base is None:
        return None
    scaled = nine_slice(
        base,
        BUTTON_0_MASTER_W,
        BUTTON_0_MASTER_H,
        margin=DEFAULT_SLICE_MARGIN,
    )
    if scaled.isNull():
        return None
    tinted = multiply_color(scaled, color)
    return None if tinted.isNull() else tinted


def _fit_to_box(pixmap: QPixmap, box_w: int, box_h: int) -> QPixmap:
    """Shrink master (2:1) to fit inside box_w×box_h, keeping aspect ratio."""
    if pixmap.isNull() or box_w < 1 or box_h < 1:
        return QPixmap()
    sw, sh = pixmap.width(), pixmap.height()
    scale = min(box_w / sw, box_h / sh)
    tw = max(1, round(sw * scale))
    th = max(1, round(sh * scale))
    return pixmap.scaled(
        tw,
        th,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def button0_fitted_size(box_w: int, box_h: int) -> tuple[int, int]:
    """Logical size of Button_0 after 2:1 fit inside box_w×box_h."""
    scale = min(box_w / BUTTON_0_MASTER_W, box_h / BUTTON_0_MASTER_H)
    return (
        max(1, round(BUTTON_0_MASTER_W * scale)),
        max(1, round(BUTTON_0_MASTER_H * scale)),
    )


def button0_pixmap(
    width: int,
    height: int,
    color: str = BUTTON_0_COLOR,
) -> QPixmap | None:
    """Master 4×2 asset → proportionally scaled to fit width×height."""
    master = button0_master(color)
    if master is None:
        return None
    fw, fh = button0_fitted_size(width, height)
    return _fit_to_box(master, fw, fh)


def button0_pixmap_scaled(
    width_scale: float = BUTTON_0_WIDTH_SCALE,
    height_scale: float = BUTTON_0_HEIGHT_SCALE,
    color: str = BUTTON_0_COLOR,
) -> QPixmap | None:
    """Export/debug: master only at given scale (default 4×2)."""
    base = button0_source()
    if base is None:
        return None
    w = max(1, round(BUTTON_0_SOURCE_SIZE * width_scale))
    h = max(1, round(BUTTON_0_SOURCE_SIZE * height_scale))
    scaled = nine_slice(base, w, h, margin=DEFAULT_SLICE_MARGIN)
    if scaled.isNull():
        return None
    return multiply_color(scaled, color)
