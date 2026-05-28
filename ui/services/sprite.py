# ui/services/sprite.py — texture-based sprite compositing pipeline
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap

from ui.services.nine_slice import DEFAULT_SLICE_MARGIN, nine_slice
from ui.services.pixmap_color import multiply_color
from ui.services.pixmap_util import pixel_size, pixmap_device_pixels
from ui.services.sheet_sprites import texture_path

ScaleMode = Literal["nine_slice", "smooth", "tile"]


@dataclass(frozen=True)
class SpriteSpec:
    """Declarative description of a single texture layer."""

    texture: str
    """Filename relative to assets/Textures/ (e.g. 'Rect_Rounded_Outline.png')."""

    width: int
    """Logical output width in pixels."""

    height: int
    """Logical output height in pixels."""

    color: str | None = None
    """Optional hex color for multiply tint. None = no tint (keep original)."""

    margin: int = DEFAULT_SLICE_MARGIN
    """9-slice corner cap in source pixels (default 170 for 512×512 assets)."""

    scale_mode: ScaleMode = "nine_slice"
    """How the source texture is scaled to (width, height)."""


@lru_cache(maxsize=64)
def _load_source(filename: str) -> QPixmap | None:
    path = texture_path(filename)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


def _scale_nine_slice(source: QPixmap, width: int, height: int, margin: int) -> QPixmap:
    return nine_slice(source, width, height, margin=margin)


def _scale_smooth(source: QPixmap, width: int, height: int) -> QPixmap:
    src = pixmap_device_pixels(source)
    return src.scaled(
        width,
        height,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def _scale_tile(source: QPixmap, width: int, height: int) -> QPixmap:
    src = pixmap_device_pixels(source)
    if src.isNull() or width < 1 or height < 1:
        return QPixmap()
    out = QPixmap(width, height)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    sw, sh = src.width(), src.height()
    for y in range(0, height, sh):
        for x in range(0, width, sw):
            painter.drawPixmap(x, y, src)
    painter.end()
    return out


def render_sprite(spec: SpriteSpec, dpr: float = 1.0) -> QPixmap:
    """Convert a SpriteSpec into a ready-to-paint QPixmap.

    Pipeline: load → scale (nine_slice / smooth / tile) → multiply_color (optional).
    The returned pixmap has logical size (spec.width × spec.height); multiply by *dpr*
    externally if you need device-pixel dimensions.
    """
    source = _load_source(spec.texture)
    if source is None:
        return QPixmap()

    w, h = spec.width, spec.height
    if w < 1 or h < 1:
        return QPixmap()

    if spec.scale_mode == "nine_slice":
        scaled = _scale_nine_slice(source, w, h, spec.margin)
    elif spec.scale_mode == "smooth":
        scaled = _scale_smooth(source, w, h)
    else:
        scaled = _scale_tile(source, w, h)

    if scaled.isNull():
        return QPixmap()

    if spec.color is not None:
        scaled = multiply_color(scaled, spec.color)

    return scaled


@lru_cache(maxsize=256)
def render_sprite_cached(
    texture: str,
    w: int,
    h: int,
    color: str | None = None,
    margin: int = DEFAULT_SLICE_MARGIN,
) -> QPixmap:
    """Cached variant of render_sprite for repeated same-size draws (e.g. icon frames)."""
    return render_sprite(SpriteSpec(texture, w, h, color=color, margin=margin))


def composite(*specs: SpriteSpec, dpr: float = 1.0) -> QPixmap:
    """Composite multiple sprite layers back-to-front into a single QPixmap.

    All specs must share the same (width, height). If they differ, the size of the
    *first* spec is used and subsequent layers are drawn at (0, 0) without scaling.

    Returns a transparent QPixmap of size (specs[0].width, specs[0].height).
    """
    if not specs:
        return QPixmap()

    w, h = specs[0].width, specs[0].height
    out = QPixmap(w, h)
    out.fill(Qt.GlobalColor.transparent)

    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    for spec in specs:
        layer = render_sprite(spec, dpr=dpr)
        if not layer.isNull():
            painter.drawPixmap(0, 0, layer)
    painter.end()

    return out
