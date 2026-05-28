# ui/services/hatch_sprites.py — hatch incubator chrome (bed / lamp / cone)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap

from ui.services.pixmap_util import configure_icon_painter, pixel_size, scale_pixmap_smooth
from ui.services.sheet_sprites import texture_path

HATCH_BED = "HatchBed.png"
HATCH_LAMP_ON = "HatchLamp.png"
HATCH_LAMP_OFF = "HatchLamp_off.png"
HATCH_LAMP_CONE = "HatchLampCone.png"


def _scale_to_box(
    pix: QPixmap,
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap:
    """Fill the PowerPoint layout cell at device resolution."""
    return scale_pixmap_smooth(
        pix,
        logical_w,
        logical_h,
        device_pixel_ratio=device_pixel_ratio,
        keep_aspect=Qt.AspectRatioMode.IgnoreAspectRatio,
    )


def _hatch_texture(
    filename: str,
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    path = texture_path(filename)
    if path is None:
        return None
    pix = QPixmap(str(path))
    if pix.isNull():
        return None
    return _scale_to_box(pix, logical_w, logical_h, device_pixel_ratio=device_pixel_ratio)


def hatch_bed_pixmap(
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    return _hatch_texture(HATCH_BED, logical_w, logical_h, device_pixel_ratio=device_pixel_ratio)


def hatch_lamp_pixmap(
    active: bool,
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    name = HATCH_LAMP_ON if active else HATCH_LAMP_OFF
    return _hatch_texture(name, logical_w, logical_h, device_pixel_ratio=device_pixel_ratio)


def hatch_cone_pixmap(
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    return _hatch_texture(HATCH_LAMP_CONE, logical_w, logical_h, device_pixel_ratio=device_pixel_ratio)


def center_pixmap(
    pix: QPixmap | None,
    logical_w: int,
    logical_h: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    """Center a (possibly HiDPI) pixmap inside a logical box."""
    if pix is None or pix.isNull():
        return None
    pw = pixel_size(logical_w, device_pixel_ratio)
    ph = pixel_size(logical_h, device_pixel_ratio)
    canvas = QPixmap(pw, ph)
    canvas.fill(Qt.GlobalColor.transparent)
    canvas.setDevicePixelRatio(device_pixel_ratio)
    painter = QPainter(canvas)
    configure_icon_painter(painter)
    sw, sh = pix.width(), pix.height()
    painter.drawPixmap((pw - sw) // 2, (ph - sh) // 2, pix)
    painter.end()
    return canvas
