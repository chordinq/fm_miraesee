# ui/widgets/skill_tile.py — circular skill icon + level + shard bar
from __future__ import annotations

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.widgets.selectable_widget import SelectableWidget

from ui.theme.metrics import (
    EQUIPPED_BADGE_SKILL,
    SKILL_CIRCLE_SIZE,
    SKILL_TILE_H,
    SKILL_TILE_W,
    TILE_CAPTION_OVERLAP,
)
from ui.services.collection_entries import CollectionTileData
from ui.widgets.icon_with_level import IconWithLevel
from ui.widgets.outlined_label import tile_caption_label
from ui.widgets.icon_frames import SkillIconDisc
from ui.widgets.skill_shard_bar import SkillShardBar


class SkillCollectionTile(SelectableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(SKILL_TILE_W, SKILL_TILE_H)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 4, 0, 0)
        layout.setSpacing(4)
        layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

        self._circle = SkillIconDisc(SKILL_CIRCLE_SIZE)
        self._level = tile_caption_label()
        self._icon_stack = IconWithLevel(
            self._circle,
            self._level,
            tile_w=SKILL_TILE_W,
            icon_size=SKILL_CIRCLE_SIZE,
            overlap=TILE_CAPTION_OVERLAP,
            equipped_placement=EQUIPPED_BADGE_SKILL,
        )
        layout.addWidget(self._icon_stack, 0, Qt.AlignmentFlag.AlignHCenter)

        self._shards = SkillShardBar()
        layout.addWidget(self._shards, 0, Qt.AlignmentFlag.AlignHCenter)

    def set_data(self, data: CollectionTileData) -> None:
        fill = data.frame_color or data.border_color
        self._circle.set_content(tint_color=fill, skill_pixmap=data.pixmap)
        self._level.setText(data.meta)
        self._icon_stack.set_equipped(data.equipped)
        self._icon_stack.refresh_geometry()
        self._shards.set_progress(data.shard_current, data.shard_max)

    def sizeHint(self) -> QSize:  # noqa: D102
        return QSize(SKILL_TILE_W, SKILL_TILE_H)
