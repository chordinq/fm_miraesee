# ui/widgets/icon_frames.py — QWidget hosts that delegate to ui.paint.item_icons
from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import QPainter, QPixmap
from PySide6.QtWidgets import QWidget

from ui.paint.item_icons import (
    paint_equipment_icon,
    paint_mount_icon,
    paint_pet_icon,
    paint_skill_icon,
)

# Legacy alias (was ui.widgets.skill_icon_disc)
paint_skill_icon_disc = paint_skill_icon

FramedIconKind = Literal["pet", "mount"]


class SkillIconDisc(QWidget):
    """Circular skill icon (tinted plate + art + outline ring)."""

    def __init__(self, size: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._tint_color = "#7a7a72"
        self._skill_pixmap: QPixmap | None = None
        self._selected = False

    def set_content(self, *, tint_color: str, skill_pixmap: QPixmap | None) -> None:
        self._tint_color = tint_color
        self._skill_pixmap = skill_pixmap
        self.update()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        paint_skill_icon(
            painter,
            self.rect(),
            tint_color=self._tint_color,
            skill_pixmap=self._skill_pixmap,
            selected=self._selected,
            device_pixel_ratio=self.devicePixelRatioF(),
        )


class RarityFramedIcon(QWidget):
    """Rounded rarity frame for pet or mount sprites."""

    def __init__(
        self,
        size: int,
        *,
        kind: FramedIconKind = "pet",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._kind = kind
        self._frame_color = "#4db84a"
        self._pixmap: QPixmap | None = None
        self._selected = False

    def set_content(self, *, frame_color: str, pixmap: QPixmap | None) -> None:
        self._frame_color = frame_color
        self._pixmap = pixmap
        self.update()

    def set_selected(self, selected: bool) -> None:
        self._selected = selected
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        dpr = self.devicePixelRatioF()
        paint_fn = paint_pet_icon if self._kind == "pet" else paint_mount_icon
        paint_fn(
            painter,
            self.rect(),
            frame_color=self._frame_color,
            pixmap=self._pixmap,
            selected=self._selected,
            device_pixel_ratio=dpr,
        )


class EquipmentIconFrame(QWidget):
    """Forge equipment cell icon (age-colored rounded frame)."""

    def __init__(self, size: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(size, size)
        self._frame_color = "#2a3040"
        self._pixmap: QPixmap | None = None

    def set_content(self, *, frame_color: str, pixmap: QPixmap | None) -> None:
        self._frame_color = frame_color
        self._pixmap = pixmap
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        paint_equipment_icon(
            painter,
            self.rect(),
            frame_color=self._frame_color,
            pixmap=self._pixmap,
            device_pixel_ratio=self.devicePixelRatioF(),
        )
