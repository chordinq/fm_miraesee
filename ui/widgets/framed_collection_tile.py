# ui/widgets/framed_collection_tile.py — pet/mount tile with rounded rarity frame + clipped sprite
from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.widgets.selectable_widget import SelectableWidget

from ui.theme.metrics import (
    EQUIPPED_BADGE_PET_MOUNT,
    FRAME_SIZE,
    FRAMED_TILE_H,
    FRAMED_TILE_W,
    TILE_CAPTION_OVERLAP,
)
from ui.services.collection_entries import CollectionTileData
from ui.widgets.icon_frames import FramedIconKind, RarityFramedIcon
from ui.widgets.icon_with_level import IconWithLevel
from ui.widgets.outlined_label import tile_caption_label


class FramedCollectionTile(SelectableWidget):
    def __init__(self, *, kind: FramedIconKind = "pet", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(FRAMED_TILE_W, FRAMED_TILE_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(0)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._frame = RarityFramedIcon(FRAME_SIZE, kind=kind)
        self._caption = tile_caption_label()
        self._icon_stack = IconWithLevel(
            self._frame,
            self._caption,
            tile_w=FRAMED_TILE_W,
            icon_size=FRAME_SIZE,
            overlap=TILE_CAPTION_OVERLAP,
            equipped_placement=EQUIPPED_BADGE_PET_MOUNT,
        )
        layout.addWidget(self._icon_stack, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_data(self, data: CollectionTileData) -> None:
        frame_color = data.frame_color or data.border_color
        self._frame.set_content(
            frame_color=frame_color,
            pixmap=data.pixmap,
        )
        self._caption.setText(data.meta)
        self._icon_stack.set_equipped(data.equipped)
        self._icon_stack.refresh_geometry()

    def sizeHint(self) -> QSize:  # noqa: D102
        return QSize(FRAMED_TILE_W, FRAMED_TILE_H)
