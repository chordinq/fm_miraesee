# ui/views/collection_view.py — scrollable collection grid (skill / pet / mount)
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.constants.colors import BG, COLLECTION_BG
from ui.constants.layout import (
    COLLECTION_GRID_PAD_TOP,
    COLLECTION_PANEL_PAD_BOTTOM,
    COLLECTION_PANEL_PAD_LEFT,
    COLLECTION_PANEL_PAD_RIGHT,
    COLLECTION_PANEL_PAD_TOP,
    FRAMED_GRID_MARGIN_H,
    GRID_COLS,
    GRID_GAP,
    GRID_MARGIN,
    collection_panel_width,
)
from ui.constants.styles import muted_label_style
from ui.services.collection_entries import CollectionTileData
from ui.services.session import Session
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
) -> None:
    body_layout = QVBoxLayout(body)
    body_layout.setContentsMargins(0, 0, 0, 0)
    body_layout.setSpacing(0)

    if not entries:
        hint = QLabel(empty_hint)
        hint.setStyleSheet(muted_label_style(padding="16px"))
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        body_layout.addStretch(1)
        body_layout.addWidget(hint)
        body_layout.addStretch(1)
        return

    grid_host = QWidget()
    grid_host.setStyleSheet("background: transparent;")
    grid_host.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
    grid = QGridLayout(grid_host)
    margin_h = grid_margin_h if grid_margin_h is not None else GRID_MARGIN
    grid.setContentsMargins(margin_h, COLLECTION_GRID_PAD_TOP, margin_h, GRID_MARGIN)
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
            tile = FramedCollectionTile()
        else:
            tile = CollectionTile()
        tile.set_data(tile_data)
        grid.addWidget(
            tile,
            i // GRID_COLS,
            i % GRID_COLS,
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
        )
    body_layout.addWidget(
        grid_host,
        0,
        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop,
    )


class CollectionView(QWidget):
    """Left column: full tab height in #C0C0C0; optional black hatch strip at bottom (pet)."""

    def __init__(
        self,
        session: Session,
        *,
        entry_builder: Callable[[PlayerModel], list[CollectionTileData]],
        empty_hint: str,
        grid_gap: int | None = None,
        grid_h_gap: int | None = None,
        grid_v_gap: int | None = None,
        grid_margin_h: int | None = None,
        scroll_max_height: int | None = None,
        bottom_widget: QWidget | None = None,
        collection_panel: bool = True,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.session = session
        self._entry_builder = entry_builder
        self._empty_hint = empty_hint
        self._grid_gap = grid_gap
        self._grid_h_gap = grid_h_gap
        self._grid_v_gap = grid_v_gap
        self._margin_h = grid_margin_h if grid_margin_h is not None else FRAMED_GRID_MARGIN_H
        self._panel: QWidget | None = None
        self._scroll: QScrollArea | None = None
        margin_h = self._margin_h
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background-color: {BG};")

        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        self._scroll = scroll
        scroll.setObjectName("CollectionScroll")
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea#CollectionScroll {{ background-color: {COLLECTION_BG}; border: none; }}"
        )
        capped_scroll = scroll_max_height is not None
        if capped_scroll:
            scroll.setMaximumHeight(scroll_max_height)
            scroll.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        else:
            scroll.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )

        body = QWidget()
        body.setStyleSheet("background: transparent;")
        populate_collection_body(
            body,
            entries=entry_builder(session.player),
            empty_hint=empty_hint,
            grid_gap=grid_gap,
            grid_h_gap=grid_h_gap,
            grid_v_gap=grid_v_gap,
            grid_margin_h=margin_h,
        )
        scroll.setWidget(body)

        if not collection_panel:
            root.addWidget(scroll, 1)
            if bottom_widget is not None:
                root.addWidget(bottom_widget, 0)
            root.addStretch(1)
            return

        panel = QWidget()
        panel.setObjectName("CollectionPanel")
        self._panel = panel
        panel.setFixedWidth(collection_panel_width(margin_h))
        panel.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        panel.setStyleSheet(
            f"QWidget#CollectionPanel {{ background-color: {COLLECTION_BG}; }}"
        )

        panel_layout = QVBoxLayout(panel)
        panel_layout.setContentsMargins(0, 0, 0, 0)
        panel_layout.setSpacing(0)

        top = QWidget()
        top.setStyleSheet("background: transparent;")
        top_layout = QVBoxLayout(top)
        top_layout.setContentsMargins(
            COLLECTION_PANEL_PAD_LEFT,
            COLLECTION_PANEL_PAD_TOP,
            COLLECTION_PANEL_PAD_RIGHT,
            0 if bottom_widget is not None else COLLECTION_PANEL_PAD_BOTTOM,
        )
        top_layout.setSpacing(0)
        if capped_scroll:
            top_layout.addWidget(scroll, 0)
            filler = QWidget()
            filler.setObjectName("CollectionFiller")
            filler.setStyleSheet(f"background-color: {COLLECTION_BG};")
            filler.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Expanding,
            )
            top_layout.addWidget(filler, 1)
        else:
            top_layout.addWidget(scroll, 1)
        panel_layout.addWidget(top, 1)

        if bottom_widget is not None:
            bottom_widget.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            panel_layout.addWidget(bottom_widget, 0)

        root.addWidget(panel, 0)
        root.addStretch(1)
        self._sync_panel_height()

    def _sync_panel_height(self) -> None:
        if self._panel is not None:
            self._panel.setMinimumHeight(self.height())
            self._panel.setMaximumHeight(self.height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_panel_height()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_panel_height()

    def refresh_locale(self) -> None:
        if self._scroll is None:
            return
        old = self._scroll.takeWidget()
        if old is not None:
            old.deleteLater()
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        populate_collection_body(
            body,
            entries=self._entry_builder(self.session.player),
            empty_hint=self._empty_hint,
            grid_gap=self._grid_gap,
            grid_h_gap=self._grid_h_gap,
            grid_v_gap=self._grid_v_gap,
            grid_margin_h=self._margin_h,
        )
        self._scroll.setWidget(body)
