# ui/paint/item_icons.py — draw skill / pet / mount / equipment icons with QPainter
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen, QPixmap

from ui.theme.metrics import FRAME_BORDER, FRAME_RADIUS
from ui.services.pixmap_util import configure_icon_painter, prepare_pixmap_for_paint, scale_pixmap_smooth
from ui.services.pixmap_util import dpr_cache_key
from ui.services.sheet_sprites import skill_disc_plate_pixmap, skill_disc_ring_pixmap
from ui.services.sprite import render_sprite_cached

_TEXTURE_FILLED = "Rect_Rounded_Filled_Outline.png"
_TEXTURE_OUTLINE = "Rect_Rounded_Outline.png"
_BORDER_NORMAL = "#000000"
_BORDER_SELECTED = "#ffffff"


def _square_target(rect: QRect | QRectF) -> QRectF:
    size = min(rect.width(), rect.height())
    x = rect.x() + (rect.width() - size) / 2
    y = rect.y() + (rect.height() - size) / 2
    return QRectF(x, y, size, size)


def _target_rect_i(target: QRectF) -> QRect:
    return QRect(
        int(round(target.x())),
        int(round(target.y())),
        int(round(target.width())),
        int(round(target.height())),
    )


def _draw_pixmap_in_square(
    painter: QPainter,
    target: QRectF,
    pixmap: QPixmap,
    *,
    device_pixel_ratio: float,
) -> None:
    pm = prepare_pixmap_for_paint(pixmap, device_pixel_ratio)
    tr = _target_rect_i(target)
    # PySide6 has no drawPixmap(QRectF, QPixmap) — use the scaling overload.
    painter.drawPixmap(tr.x(), tr.y(), tr.width(), tr.height(), pm)


def _rounded_plate(
    rect: QRect | QRectF,
    *,
    border_width: float,
    border_radius: float,
) -> tuple[QRectF, QPainterPath]:
    if isinstance(rect, QRectF):
        bounds = rect
    else:
        bounds = QRectF(rect)
    inset = border_width / 2
    plate = QRectF(
        bounds.x() + inset,
        bounds.y() + inset,
        bounds.width() - border_width,
        bounds.height() - border_width,
    )
    path = QPainterPath()
    path.addRoundedRect(plate, border_radius, border_radius)
    return plate, path


def _draw_cover_sprite(
    painter: QPainter,
    path: QPainterPath,
    plate: QRectF,
    pixmap: QPixmap,
    *,
    device_pixel_ratio: float,
) -> None:
    painter.setClipPath(path)
    sw = pixmap.width() / max(pixmap.devicePixelRatio(), 1.0)
    sh = pixmap.height() / max(pixmap.devicePixelRatio(), 1.0)
    scale = max(plate.width() / sw, plate.height() / sh)
    dw = sw * scale
    dh = sh * scale
    x = plate.x() + (plate.width() - dw) / 2
    y = plate.y() + (plate.height() - dh) / 2
    target = QRectF(x, y, dw, dh)
    if abs(pixmap.devicePixelRatio() - device_pixel_ratio) > 0.01:
        scaled = scale_pixmap_smooth(
            pixmap,
            int(round(dw)),
            int(round(dh)),
            device_pixel_ratio=device_pixel_ratio,
            keep_aspect=Qt.AspectRatioMode.IgnoreAspectRatio,
        )
        tr = _target_rect_i(target)
        painter.drawPixmap(tr.x(), tr.y(), tr.width(), tr.height(), scaled)
    else:
        tr = _target_rect_i(target)
        painter.drawPixmap(tr.x(), tr.y(), tr.width(), tr.height(), pixmap)
    painter.setClipping(False)


def _skill_sprite_for_paint(
    skill_pixmap: QPixmap,
    logical_size: int,
    *,
    device_pixel_ratio: float,
) -> QPixmap:
    if abs(skill_pixmap.devicePixelRatio() - device_pixel_ratio) < 0.01:
        logical_w = skill_pixmap.width() / max(skill_pixmap.devicePixelRatio(), 1.0)
        if abs(logical_w - logical_size) < 0.5:
            return skill_pixmap
    return scale_pixmap_smooth(
        skill_pixmap,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
        keep_aspect=Qt.AspectRatioMode.IgnoreAspectRatio,
    )


def paint_skill_icon(
    painter: QPainter,
    rect: QRect | QRectF,
    *,
    tint_color: str,
    skill_pixmap: QPixmap | None,
    selected: bool = False,
    device_pixel_ratio: float = 1.0,
) -> None:
    """SmallRoundButton rarity tint → skill art → Circle_Outline ring."""
    configure_icon_painter(painter)
    target = _square_target(rect)
    logical_size = max(1, int(round(target.width())))
    dpr_key = dpr_cache_key(device_pixel_ratio)

    plate = skill_disc_plate_pixmap(logical_size, tint_color, dpr_key)
    if plate is not None and not plate.isNull():
        _draw_pixmap_in_square(painter, target, plate, device_pixel_ratio=device_pixel_ratio)

    if skill_pixmap is not None and not skill_pixmap.isNull():
        sprite = _skill_sprite_for_paint(
            skill_pixmap,
            logical_size,
            device_pixel_ratio=device_pixel_ratio,
        )
        _draw_pixmap_in_square(painter, target, sprite, device_pixel_ratio=device_pixel_ratio)

    ring_color = "#ffffff" if selected else "#000000"
    ring = skill_disc_ring_pixmap(logical_size, ring_color, dpr_key)
    if ring is not None and not ring.isNull():
        _draw_pixmap_in_square(painter, target, ring, device_pixel_ratio=device_pixel_ratio)


def _draw_frame_texture(
    painter: QPainter,
    rect: QRectF,
    texture: str,
    color: str,
) -> None:
    """Draw a 9-sliced frame texture tinted with color; falls back silently if unavailable."""
    w, h = max(1, int(round(rect.width()))), max(1, int(round(rect.height())))
    pix = render_sprite_cached(texture, w, h, color)
    if not pix.isNull():
        painter.drawPixmap(int(round(rect.x())), int(round(rect.y())), pix)


def paint_rarity_framed_icon(
    painter: QPainter,
    rect: QRect | QRectF,
    *,
    frame_color: str,
    pixmap: QPixmap | None,
    selected: bool = False,
    border_width: float = FRAME_BORDER,
    border_radius: float = FRAME_RADIUS,
    selected_border_width: float = 3,
    device_pixel_ratio: float = 1.0,
) -> None:
    """Rounded rarity plate with cover-cropped sprite and texture-based border."""
    configure_icon_painter(painter)
    bounds = QRectF(rect) if isinstance(rect, QRect) else rect
    plate, clip_path = _rounded_plate(rect, border_width=border_width, border_radius=border_radius)

    # Background fill (texture, tinted with rarity color)
    bg = render_sprite_cached(_TEXTURE_FILLED, max(1, int(round(bounds.width()))), max(1, int(round(bounds.height()))), frame_color)
    if not bg.isNull():
        painter.drawPixmap(int(round(bounds.x())), int(round(bounds.y())), bg)
    else:
        # Fallback: QPainter fill
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(frame_color))
        painter.drawPath(clip_path)

    # Cover-crop sprite (still needs clip path)
    if pixmap is not None and not pixmap.isNull():
        _draw_cover_sprite(
            painter,
            clip_path,
            plate,
            pixmap,
            device_pixel_ratio=device_pixel_ratio,
        )

    # Border overlay (texture, tinted black or white)
    border_color = _BORDER_SELECTED if selected else _BORDER_NORMAL
    bw, bh = max(1, int(round(bounds.width()))), max(1, int(round(bounds.height())))
    border_pix = render_sprite_cached(_TEXTURE_OUTLINE, bw, bh, border_color)
    if not border_pix.isNull():
        painter.drawPixmap(int(round(bounds.x())), int(round(bounds.y())), border_pix)
    else:
        # Fallback: QPen border
        edge_w = selected_border_width if selected else border_width
        painter.setPen(QPen(QColor(border_color), edge_w))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(clip_path)


def paint_pet_icon(
    painter: QPainter,
    rect: QRect | QRectF,
    *,
    frame_color: str,
    pixmap: QPixmap | None,
    selected: bool = False,
    border_width: float = FRAME_BORDER,
    border_radius: float = FRAME_RADIUS,
    device_pixel_ratio: float = 1.0,
) -> None:
    """Pet collection / equipped icon (rounded rarity frame)."""
    paint_rarity_framed_icon(
        painter,
        rect,
        frame_color=frame_color,
        pixmap=pixmap,
        selected=selected,
        border_width=border_width,
        border_radius=border_radius,
        device_pixel_ratio=device_pixel_ratio,
    )


def paint_mount_icon(
    painter: QPainter,
    rect: QRect | QRectF,
    *,
    frame_color: str,
    pixmap: QPixmap | None,
    selected: bool = False,
    border_width: float = FRAME_BORDER,
    border_radius: float = FRAME_RADIUS,
    device_pixel_ratio: float = 1.0,
) -> None:
    """Mount collection / equipped icon (rounded rarity frame)."""
    paint_rarity_framed_icon(
        painter,
        rect,
        frame_color=frame_color,
        pixmap=pixmap,
        selected=selected,
        border_width=border_width,
        border_radius=border_radius,
        device_pixel_ratio=device_pixel_ratio,
    )


def paint_equipment_icon(
    painter: QPainter,
    rect: QRect | QRectF,
    *,
    frame_color: str,
    pixmap: QPixmap | None,
    border_width: float = FRAME_BORDER,
    border_radius: float = FRAME_RADIUS,
    device_pixel_ratio: float = 1.0,
) -> None:
    """Forge equipment slot icon (rounded age-colored frame, black border)."""
    paint_rarity_framed_icon(
        painter,
        rect,
        frame_color=frame_color,
        pixmap=pixmap,
        selected=False,
        border_width=border_width,
        border_radius=border_radius,
        device_pixel_ratio=device_pixel_ratio,
    )
