# ui/widgets/collection_tile.py — icon tile for skill / egg grids
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from ui.constants.layout import COLLECTION_ICON_SIZE, COLLECTION_TILE_H, COLLECTION_TILE_W
from ui.constants.styles import collection_tile_style
from ui.services.collection_entries import CollectionTileData


class CollectionTile(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("CollectionTile")
        self._tile_w = COLLECTION_TILE_W
        self._tile_h = COLLECTION_TILE_H
        self._icon_size = COLLECTION_ICON_SIZE
        self._icon_area_h = COLLECTION_ICON_SIZE
        self._icon_top_margin = 3
        self.setFixedSize(self._tile_w, self._tile_h)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(3, self._icon_top_margin, 3, 2)
        self._layout.setSpacing(1)

        self._icon_host = QWidget()
        self._icon_host.setStyleSheet("background: transparent;")
        host_layout = QVBoxLayout(self._icon_host)
        host_layout.setContentsMargins(0, 0, 0, 0)
        host_layout.setSpacing(0)

        self._icon = QLabel()
        self._icon.setObjectName("CollectionIcon")
        self._icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        host_layout.addWidget(self._icon, 0, Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._icon_host, 0, Qt.AlignmentFlag.AlignHCenter)

        self._name = QLabel("—")
        self._name.setObjectName("CollectionName")
        self._name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._name.setWordWrap(True)
        self._layout.addWidget(self._name)

        self._meta = QLabel("")
        self._meta.setObjectName("CollectionMeta")
        self._meta.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._layout.addWidget(self._meta)

        self._apply_geometry()

    def _apply_geometry(self) -> None:
        self.setFixedSize(self._tile_w, self._tile_h)
        self._layout.setContentsMargins(0, self._icon_top_margin, 0, 2)
        self._icon_host.setFixedSize(self._icon_size, self._icon_area_h)
        self._icon.setFixedSize(self._icon_size, self._icon_size)

    def set_data(self, data: CollectionTileData) -> None:
        if data.tile_w is not None:
            self._tile_w = data.tile_w
        if data.tile_h is not None:
            self._tile_h = data.tile_h
        if data.icon_size is not None:
            self._icon_size = data.icon_size
        if data.icon_area_h is not None:
            self._icon_area_h = data.icon_area_h
        else:
            self._icon_area_h = self._icon_size
        if data.icon_top_margin is not None:
            self._icon_top_margin = data.icon_top_margin
        self._apply_geometry()

        filled = data.pixmap is not None
        self.setStyleSheet(collection_tile_style(border_color=data.border_color, filled=filled))
        if data.pixmap is not None:
            self._icon.setStyleSheet("")
            self._icon.setPixmap(data.pixmap)
            self._icon.setText("")
        else:
            self._icon.clear()
            self._icon.setText("·")
            self._icon.setStyleSheet(f"color: {data.border_color}; font-size: 16px; background: transparent;")
        if data.name:
            self._name.setText(data.name)
            self._name.show()
        else:
            self._name.hide()
        self._meta.setText(data.meta)
        self._meta.setVisible(bool(data.meta))
        if data.meta and not data.name:
            self._meta.setStyleSheet(
                "color: #ffffff; font-size: 11px; font-weight: bold; background: transparent;"
            )
        else:
            self._meta.setStyleSheet(
                "color: #8a8a8a; font-size: 8px; background: transparent;"
            )
