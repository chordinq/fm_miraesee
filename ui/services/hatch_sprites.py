# ui/services/hatch_sprites.py — hatch incubator chrome (bed / lamp / cone)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap

from ui.services.sheet_sprites import texture_path

HATCH_BED = "HatchBed.png"
HATCH_LAMP_ON = "HatchLamp.png"
HATCH_LAMP_OFF = "HatchLamp_off.png"
HATCH_LAMP_CONE = "HatchLampCone.png"


def _center_in_box(pix: QPixmap, width: int, height: int) -> QPixmap:
    """Scale with aspect ratio, then center on a transparent box (fixes PNG padding skew)."""
    scaled = pix.scaled(
        width,
        height,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
    canvas = QPixmap(width, height)
    canvas.fill(Qt.GlobalColor.transparent)
    painter = QPainter(canvas)
    x = (width - scaled.width()) // 2
    y = (height - scaled.height()) // 2
    painter.drawPixmap(x, y, scaled)
    painter.end()
    return canvas


def _hatch_texture(filename: str, width: int, height: int) -> QPixmap | None:
    path = texture_path(filename)
    if path is None:
        return None
    pix = QPixmap(str(path))
    if pix.isNull():
        return None
    return _center_in_box(pix, width, height)


def hatch_bed_pixmap(width: int, height: int) -> QPixmap | None:
    return _hatch_texture(HATCH_BED, width, height)


def hatch_lamp_pixmap(active: bool, width: int, height: int) -> QPixmap | None:
    name = HATCH_LAMP_ON if active else HATCH_LAMP_OFF
    return _hatch_texture(name, width, height)


def hatch_cone_pixmap(width: int, height: int) -> QPixmap | None:
    return _hatch_texture(HATCH_LAMP_CONE, width, height)


def center_pixmap(pix: QPixmap | None, width: int, height: int) -> QPixmap | None:
    if pix is None or pix.isNull():
        return None
    return _center_in_box(pix, width, height)
