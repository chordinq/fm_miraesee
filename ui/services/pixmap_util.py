# ui/services/pixmap_util.py — HiDPI-aware pixmap scaling for crisp UI icons
from __future__ import annotations

from PySide6.QtCore import Qt, QRect, QRectF
from PySide6.QtGui import QPainter, QPixmap


def pixel_size(logical_size: int, device_pixel_ratio: float = 1.0) -> int:
    """Logical widget size → device-pixel count for pixmap buffers."""
    return max(1, round(logical_size * device_pixel_ratio))


def scale_pixmap_smooth(
    pixmap: QPixmap,
    logical_w: int,
    logical_h: int | None = None,
    *,
    device_pixel_ratio: float = 1.0,
    keep_aspect: Qt.AspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio,
) -> QPixmap:
    """Scale once at device resolution and tag DPR so QPainter does not stretch."""
    if pixmap.isNull():
        return pixmap
    pw = pixel_size(logical_w, device_pixel_ratio)
    ph = pixel_size(logical_h if logical_h is not None else logical_w, device_pixel_ratio)
    scaled = pixmap.scaled(
        pw,
        ph,
        keep_aspect,
        Qt.TransformationMode.SmoothTransformation,
    )
    if device_pixel_ratio > 0:
        scaled.setDevicePixelRatio(device_pixel_ratio)
    return scaled


def pixmap_device_pixels(pixmap: QPixmap) -> QPixmap:
    """Flatten to 1:1 device pixels (DPR metadata breaks DestinationIn compositing)."""
    if pixmap.isNull():
        return pixmap
    copy = QPixmap.fromImage(pixmap.toImage())
    copy.setDevicePixelRatio(1.0)
    return copy


def prepare_pixmap_for_paint(pixmap: QPixmap, device_pixel_ratio: float) -> QPixmap:
    """Normalize pixmap before QPainter.drawPixmap scaling overload."""
    _ = device_pixel_ratio  # logical target rect already defines output size
    return pixmap_device_pixels(pixmap)


def default_device_pixel_ratio() -> float:
    from PySide6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        return 1.0
    screen = app.primaryScreen()
    if screen is None:
        return 1.0
    return float(screen.devicePixelRatio())


def draw_pixmap_in_rect(
    painter: QPainter,
    target: QRect | QRectF,
    pixmap: QPixmap,
    *,
    source: QRect | None = None,
) -> None:
    """PySide6-safe drawPixmap (no QRectF + QPixmap-only overload)."""
    if pixmap.isNull():
        return
    x = int(round(target.x()))
    y = int(round(target.y()))
    w = max(1, int(round(target.width())))
    h = max(1, int(round(target.height())))
    if source is None:
        painter.drawPixmap(x, y, w, h, pixmap)
    else:
        painter.drawPixmap(x, y, w, h, pixmap, source.x(), source.y(), source.width(), source.height())


def configure_icon_painter(painter: QPainter) -> None:
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)


def dpr_cache_key(device_pixel_ratio: float) -> int:
    """Stable int key for lru_cache (two decimal places)."""
    return max(100, round(device_pixel_ratio * 100))
