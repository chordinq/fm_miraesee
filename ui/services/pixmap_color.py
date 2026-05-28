# ui/services/pixmap_color.py — multiply tint (black unchanged, white → full color)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPixmap

from ui.services.pixmap_util import pixmap_device_pixels


def multiply_color(image: QPixmap, color: str) -> QPixmap:
    """
    Tint a grayscale UI texture with a hex color.

    Black stays black; white receives the full color; mid-tones darken proportionally.
    """
    base = pixmap_device_pixels(image)
    if base.isNull():
        return QPixmap()

    out = QPixmap(base.size())
    out.fill(Qt.GlobalColor.transparent)

    color_layer = QPixmap(base.size())
    color_layer.fill(QColor(color))

    mask_painter = QPainter(color_layer)
    mask_painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
    mask_painter.drawPixmap(0, 0, base)
    mask_painter.end()

    painter = QPainter(out)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.drawPixmap(0, 0, base)
    painter.setCompositionMode(QPainter.CompositionMode_Multiply)
    painter.drawPixmap(0, 0, color_layer)
    painter.end()
    return out
