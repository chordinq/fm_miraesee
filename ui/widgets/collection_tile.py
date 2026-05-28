# ui/widgets/collection_tile.py — egg tile (icon + 알 / Egg / 卵 caption)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.widgets.selectable_widget import SelectableWidget

from ui.theme.metrics import (
    EGG_ICON_SIZE,
    EGG_ICON_TOP_MARGIN,
    EGG_TILE_W,
    TILE_CAPTION_OVERLAP,
)
from ui.theme.builders import collection_tile_style
from ui.services.collection_entries import CollectionTileData
from ui.widgets.icon_with_level import IconWithLevel
from ui.widgets.outlined_label import tile_caption_label


class CollectionTile(SelectableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CollectionTile")
        self._tile_w = EGG_TILE_W
        self._tile_h = 80
        self._icon_size = EGG_ICON_SIZE
        self._icon_top_margin = EGG_ICON_TOP_MARGIN

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, self._icon_top_margin, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._icon = QLabel()
        self._icon.setObjectName("CollectionIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._icon.setFixedSize(self._icon_size, self._icon_size)

        self._caption = tile_caption_label()
        self._caption.setObjectName("EggCaption")

        self._icon_stack = IconWithLevel(
            self._icon,
            self._caption,
            tile_w=self._tile_w,
            icon_size=self._icon_size,
            overlap=TILE_CAPTION_OVERLAP,
        )
        layout.addWidget(self._icon_stack, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_data(self, data: CollectionTileData) -> None:
        if data.tile_w is not None:
            self._tile_w = data.tile_w
        if data.icon_size is not None:
            self._icon_size = data.icon_size
        if data.icon_top_margin is not None:
            self._icon_top_margin = EGG_ICON_TOP_MARGIN

        filled = data.pixmap is not None
        self.setStyleSheet(collection_tile_style(border_color=data.border_color, filled=filled))

        if data.pixmap is not None:
            self._icon.setStyleSheet("")
            self._icon.setPixmap(data.pixmap)
            self._icon.setText("")
        else:
            self._icon.clear()
            self._icon.setText("·")
            self._icon.setStyleSheet(
                f"color: {data.border_color}; font-size: 16px; background: transparent;"
            )

        self._caption.setText(data.meta)
        self._caption.setVisible(bool(data.meta))

        cap_w = self._caption.caption_width()
        stack_w = max(self._tile_w, cap_w)
        self._icon_stack.set_tile_width(stack_w)

        self._tile_w = stack_w
        self._tile_h = self._icon_top_margin + self._icon_stack.height() + 2
        self.setFixedSize(self._tile_w, self._tile_h)
