# ui/services/nine_slice.py — 9-slice resize (corners fixed, center stretched)
from __future__ import annotations

from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QPixmap

from ui.services.pixmap_util import pixmap_device_pixels

# Button_0.png (512×512): safe corner cap in source pixels
DEFAULT_SLICE_MARGIN = 170


def _source_margin(sw: int, sh: int, margin: int) -> int:
    cap = min(sw, sh) // 2 - 1
    if cap < 1:
        return 0
    return max(1, min(margin, cap))


def _target_margin(sw: int, sh: int, tw: int, th: int, margin: int) -> int:
    """Target corner size: scales down with output, never larger than source cap."""
    sm = _source_margin(sw, sh, margin)
    if sm < 1:
        return 0
    mx = round(margin * tw / sw)
    my = round(margin * th / sh)
    cap = min(tw // 2 - 1, th // 2 - 1)
    if cap < 1:
        return 0
    return max(1, min(mx, my, sm, cap))


def _draw_nine_slice(
    painter: QPainter,
    *,
    tx: int,
    ty: int,
    tw: int,
    th: int,
    source: QPixmap,
    margin: int,
) -> None:
    sw, sh = source.width(), source.height()
    sm = _source_margin(sw, sh, margin)
    tm = _target_margin(sw, sh, tw, th, margin)
    if sm < 1 or tm < 1 or tw <= tm * 2 or th <= tm * 2:
        painter.drawPixmap(QRect(tx, ty, tw, th), source, QRect(0, 0, sw, sh))
        return

    painter.drawPixmap(QRect(tx, ty, tm, tm), source, QRect(0, 0, sm, sm))
    painter.drawPixmap(
        QRect(tx + tm, ty, tw - tm * 2, tm),
        source,
        QRect(sm, 0, sw - sm * 2, sm),
    )
    painter.drawPixmap(QRect(tx + tw - tm, ty, tm, tm), source, QRect(sw - sm, 0, sm, sm))
    painter.drawPixmap(
        QRect(tx, ty + tm, tm, th - tm * 2),
        source,
        QRect(0, sm, sm, sh - sm * 2),
    )
    painter.drawPixmap(
        QRect(tx + tm, ty + tm, tw - tm * 2, th - tm * 2),
        source,
        QRect(sm, sm, sw - sm * 2, sh - sm * 2),
    )
    painter.drawPixmap(
        QRect(tx + tw - tm, ty + tm, tm, th - tm * 2),
        source,
        QRect(sw - sm, sm, sm, sh - sm * 2),
    )
    painter.drawPixmap(QRect(tx, ty + th - tm, tm, tm), source, QRect(0, sh - sm, sm, sm))
    painter.drawPixmap(
        QRect(tx + tm, ty + th - tm, tw - tm * 2, tm),
        source,
        QRect(sm, sh - sm, sw - sm * 2, sm),
    )
    painter.drawPixmap(
        QRect(tx + tw - tm, ty + th - tm, tm, tm),
        source,
        QRect(sw - sm, sh - sm, sm, sm),
    )


def nine_slice(
    image: QPixmap,
    width: int,
    height: int,
    *,
    margin: int = DEFAULT_SLICE_MARGIN,
) -> QPixmap:
    """Resize image to (width, height) with 9-slice scaling."""
    image = pixmap_device_pixels(image)
    if image.isNull() or width < 1 or height < 1:
        return QPixmap()

    tw, th = int(width), int(height)
    out = QPixmap(tw, th)
    out.fill(Qt.GlobalColor.transparent)
    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    _draw_nine_slice(painter, tx=0, ty=0, tw=tw, th=th, source=image, margin=margin)
    painter.end()
    return out


def nine_slice_scaled(
    image: QPixmap,
    width_scale: float,
    height_scale: float,
    *,
    margin: int = DEFAULT_SLICE_MARGIN,
) -> QPixmap:
    """Resize image by multiplying source width/height by scale factors."""
    image = pixmap_device_pixels(image)
    if image.isNull():
        return QPixmap()
    sw, sh = image.width(), image.height()
    return nine_slice(
        image,
        max(1, round(sw * width_scale)),
        max(1, round(sh * height_scale)),
        margin=margin,
    )
