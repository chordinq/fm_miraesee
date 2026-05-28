# ui/widgets/icon_with_level.py — icon + Lv caption overlapping the bottom edge
from __future__ import annotations

from PySide6.QtWidgets import QWidget

from ui.theme.metrics import EquippedBadgePlacement
from ui.widgets.equipped_badge import EquippedBadge
from ui.widgets.outlined_label import OutlinedLabel


class IconWithLevel(QWidget):
    """Stacks an icon widget and level caption; caption overlaps the icon bottom."""

    def __init__(
        self,
        icon: QWidget,
        level: OutlinedLabel,
        *,
        tile_w: int,
        icon_size: int,
        overlap: int,
        equipped_placement: EquippedBadgePlacement | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._tile_w = tile_w
        self._icon_size = icon_size
        self._overlap = overlap
        self._equipped_placement = equipped_placement
        icon.setParent(self)
        level.setParent(self)
        self._icon = icon
        self._level = level
        self._badge: EquippedBadge | None = None
        if equipped_placement is not None:
            self._badge = EquippedBadge(self)
        self.refresh_geometry()

    def set_equipped(self, equipped: bool) -> None:
        if self._badge is None:
            return
        self._badge.refresh_text()
        if equipped:
            self._badge.show()
            if self._equipped_placement is not None:
                self._badge.place(self._equipped_placement)
        else:
            self._badge.hide()

    def set_tile_width(self, width: int) -> None:
        self._tile_w = width
        self.refresh_geometry()

    def refresh_geometry(self) -> None:
        icon_h = self._icon_size
        level_h = self._level.caption_height()
        level_w = self._level.caption_width()
        stack_h = icon_h + level_h - self._overlap
        self.setFixedSize(self._tile_w, stack_h)

        icon_x = (self._tile_w - self._icon_size) // 2
        self._icon.setGeometry(icon_x, 0, self._icon_size, self._icon_size)

        level_x = (self._tile_w - level_w) // 2
        level_y = icon_h - self._overlap
        self._level.setGeometry(level_x, level_y, level_w, level_h)
        self._level.raise_()

        if self._badge is not None and self._badge.isVisible() and self._equipped_placement:
            self._badge.place(self._equipped_placement)
            self._badge.raise_()

    def resizeEvent(self, event) -> None:  # noqa: N802
        self.refresh_geometry()
        super().resizeEvent(event)
