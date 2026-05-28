# ui/views/collection/grid_body.py — build scrollable collection tile grid
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QSizePolicy, QVBoxLayout, QWidget

from ui.services.collection_entries import CollectionTileData
from ui.services.collection_selection import CollectionSelection
from ui.theme.builders import muted_label_style
from ui.theme.metrics import (
    COLLECTION_GRID_PAD_TOP,
    GRID_COLS,
    GRID_GAP,
    GRID_MARGIN,
)
from ui.widgets.collection_tile import CollectionTile
from ui.widgets.framed_collection_tile import FramedCollectionTile
from ui.widgets.skill_tile import SkillCollectionTile


def populate_collection_body(
    body: QWidget,
    *,
    entries: list[CollectionTileData],
    empty_hint: str,
    grid_gap: int | None = None,
    grid_h_gap: int | None = None,
    grid_v_gap: int | None = None,
    grid_margin_h: int | None = None,
    grid_margin_bottom: int | None = None,
    on_select: Callable[[CollectionSelection], None] | None = None,
    selected: CollectionSelection | None = None,
) -> list:
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setSpacing(0)
    tiles: list = []

    if not entries:
        hint = QLabel(empty_hint)
        hint.setStyleSheet(muted_label_style(padding="16px"))
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addStretch(1)
        body_layout.addWidget(hint)
        body_layout.addStretch(1)
        return tiles

    grid_host = QWidget()
    grid_host.setStyleSheet("background: transparent;")
    grid_host.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
    grid = QGridLayout(grid_host)
    margin_h = grid_margin_h if grid_margin_h is not None else GRID_MARGIN
    margin_bottom = grid_margin_bottom if grid_margin_bottom is not None else GRID_MARGIN
    grid.setContentsMargins(margin_h, COLLECTION_GRID_PAD_TOP, margin_h, margin_bottom)
    h_gap = grid_h_gap if grid_h_gap is not None else (grid_gap if grid_gap is not None else GRID_GAP)
    v_gap = grid_v_gap if grid_v_gap is not None else (grid_gap if grid_gap is not None else GRID_GAP)
    grid.setHorizontalSpacing(h_gap)
    grid.setVerticalSpacing(v_gap)
    for col in range(GRID_COLS):
        grid.setColumnStretch(col, 0)
    row_count = (len(entries) + GRID_COLS - 1) // GRID_COLS
    for row in range(row_count):
        grid.setRowStretch(row, 0)
    for i, tile_data in enumerate(entries):
        if tile_data.circular:
            tile = SkillCollectionTile()
        elif tile_data.framed:
            tile = FramedCollectionTile(kind=tile_data.icon_kind or "pet")
        else:
            tile = CollectionTile()
        tile.set_data(tile_data)
        if on_select is not None and tile_data.selection is not None:
            sel = tile_data.selection

            def _emit(s: CollectionSelection = sel) -> None:
                on_select(s)

            tile.clicked.connect(_emit)
        if tile_data.selection is not None:
            tile.setProperty("miraesee_selection", tile_data.selection)
        if selected is not None and tile_data.selection == selected:
            tile.set_selected(True)
        grid.addWidget(
            tile,
            i // GRID_COLS,
            i % GRID_COLS,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
        tiles.append(tile)
    body_layout.addWidget(
        grid_host,
        0,
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
    )
    return tiles
