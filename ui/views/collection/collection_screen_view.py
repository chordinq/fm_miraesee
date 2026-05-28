# ui/views/collection/collection_screen_div.py — currency pills + collection panel
from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Qt
from PySide6.QtGui import QResizeEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from core.enums import CurrencyType
from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.views.collection.footer_placement import FooterPlacement
from ui.views.collection.footer_sync import (
    as_hatch_footer,
    refresh_hatch_footer,
    sync_hatch_footer,
)
from ui.views.collection.grid_body import populate_collection_body
from ui.services.collection_entries import CollectionTileData
from ui.services.collection_selection import CollectionSelection
from features.session import Session
from ui.theme.colors import BG, COLLECTION_BG
from ui.theme.metrics import (
    COLLECTION_PANEL_PAD_BOTTOM,
    COLLECTION_PANEL_PAD_LEFT,
    COLLECTION_PANEL_PAD_RIGHT,
    COLLECTION_PANEL_PAD_TOP,
    FRAMED_GRID_MARGIN_H,
    collection_panel_width,
)
from ui.theme.metrics import currency_pill_pixel_size
from ui.widgets.currency_pill_widget import CurrencyPillWidget


class CollectionScreenView(QWidget):
    """Gray collection column on the right; currency pills live inside the panel top."""

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
        grid_margin_bottom: int | None = None,
        scroll_max_height: int | None = None,
        footer: QWidget | None = None,
        footer_placement: FooterPlacement = FooterPlacement.NONE,
        currency_left: CurrencyType | None = None,
        currency_right: CurrencyType | None = None,
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
        self._margin_bottom = grid_margin_bottom
        self._footer_placement = footer_placement
        self._hatch_footer = as_hatch_footer(footer)
        self._panel: QWidget | None = None
        self._scroll: QScrollArea | None = None
        self._selection: CollectionSelection | None = None
        self._tiles: list = []
        self._currency_pills: list[CurrencyPillWidget] = []

        if self._hatch_footer is not None:
            self._hatch_footer.row.slot_clicked.connect(self._on_tile_selected)

        margin_h = self._margin_h
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setStyleSheet(f"background-color: {BG};")

        use_full_width_footer = (
            footer_placement == FooterPlacement.FULL_WIDTH and collection_panel
        )
        has_currency = currency_left is not None or currency_right is not None
        if use_full_width_footer:
            root = QVBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)
            content_row = QHBoxLayout()
            content_row.setContentsMargins(0, 0, 0, 0)
            content_row.setSpacing(0)
        else:
            root = QHBoxLayout(self)
            root.setContentsMargins(0, 0, 0, 0)
            root.setSpacing(0)
            content_row = root

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
        self._tiles = populate_collection_body(
            body,
            entries=entry_builder(session.player),
            empty_hint=empty_hint,
            grid_gap=grid_gap,
            grid_h_gap=grid_h_gap,
            grid_v_gap=grid_v_gap,
            grid_margin_h=margin_h,
            grid_margin_bottom=self._margin_bottom,
            on_select=self._on_tile_selected,
            selected=self._selection,
        )
        scroll.setWidget(body)

        if not collection_panel:
            content_row.addWidget(scroll, 1)
            if footer is not None:
                content_row.addWidget(footer, 0)
            content_row.addStretch(1)
            root.addLayout(content_row, 1)
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
        panel_layout.setSpacing(6 if footer_placement == FooterPlacement.IN_PANEL else 0)

        if has_currency:
            _, pill_h = currency_pill_pixel_size()
            pill_wrap = QWidget()
            pill_wrap.setFixedHeight(pill_h + 10)
            pill_wrap.setStyleSheet("background: transparent;")
            pill_row = QHBoxLayout(pill_wrap)
            pill_row.setContentsMargins(
                COLLECTION_PANEL_PAD_RIGHT,
                6,
                COLLECTION_PANEL_PAD_LEFT,
                4,
            )
            pill_row.setSpacing(0)
            if currency_left is not None:
                left = CurrencyPillWidget(session.player, currency_left, panel)
                self._currency_pills.append(left)
                pill_row.addWidget(
                    left,
                    0,
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                )
            pill_row.addStretch(1)
            if currency_right is not None:
                right = CurrencyPillWidget(session.player, currency_right, panel)
                self._currency_pills.append(right)
                pill_row.addWidget(
                    right,
                    0,
                    Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
                )
            panel_layout.addWidget(pill_wrap, 0)

        top = QWidget()
        top.setStyleSheet("background: transparent;")
        top_layout = QVBoxLayout(top)
        has_in_panel_footer = footer_placement == FooterPlacement.IN_PANEL and footer is not None
        top_layout.setContentsMargins(
            COLLECTION_PANEL_PAD_RIGHT,
            COLLECTION_PANEL_PAD_TOP if not has_currency else 0,
            COLLECTION_PANEL_PAD_LEFT,
            COLLECTION_PANEL_PAD_BOTTOM if not has_in_panel_footer else 0,
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

        if has_in_panel_footer and footer is not None:
            footer.setSizePolicy(
                QSizePolicy.Policy.Expanding,
                QSizePolicy.Policy.Fixed,
            )
            panel_layout.addWidget(footer, 0)

        content_row.addStretch(1)
        content_row.addWidget(panel, 0)
        if use_full_width_footer:
            root.addLayout(content_row, 1)
            if footer is not None:
                footer.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Fixed,
                )
                root.addWidget(footer, 0)

        self._sync_panel_height()
        self._sync_hatch_bar()

    def _on_tile_selected(self, selection: CollectionSelection) -> None:
        self._selection = selection
        for tile in self._tiles:
            bound = tile.property("miraesee_selection")
            tile.set_selected(bound == selection)
        if self._hatch_footer is not None:
            self._hatch_footer.row.set_selected(selection)

    def _refresh_currency_pills(self) -> None:
        for pill in self._currency_pills:
            pill.refresh()

    def _rebuild_grid(self) -> None:
        if self._scroll is None:
            return
        old = self._scroll.takeWidget()
        if old is not None:
            old.deleteLater()
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        self._tiles = populate_collection_body(
            body,
            entries=self._entry_builder(self.session.player),
            empty_hint=self._empty_hint,
            grid_gap=self._grid_gap,
            grid_h_gap=self._grid_h_gap,
            grid_v_gap=self._grid_v_gap,
            grid_margin_h=self._margin_h,
            grid_margin_bottom=self._margin_bottom,
            on_select=self._on_tile_selected,
            selected=self._selection,
        )
        self._scroll.setWidget(body)
        self._refresh_hatch_slots()

    def _refresh_hatch_slots(self) -> None:
        refresh_hatch_footer(
            self._hatch_footer,
            self.session.player.pets.hatch_slots(),
            self._selection,
        )

    def _panel_inner_width(self) -> int:
        if self._panel is None:
            return collection_panel_width(self._margin_h)
        w = self._panel.width()
        if w > 0:
            return w
        return collection_panel_width(self._margin_h)

    def _sync_hatch_bar(self) -> None:
        sync_hatch_footer(
            self._hatch_footer,
            self._panel_inner_width(),
            grid_margin_h=self._margin_h,
        )
        self._refresh_hatch_slots()

    def _sync_panel_height(self) -> None:
        if self._panel is not None:
            self._panel.setMinimumHeight(self.height())
            self._panel.setMaximumHeight(self.height())

    def resizeEvent(self, event: QResizeEvent) -> None:  # noqa: N802
        super().resizeEvent(event)
        self._sync_panel_height()
        self._sync_hatch_bar()

    def showEvent(self, event) -> None:  # noqa: N802
        super().showEvent(event)
        self._sync_panel_height()
        self._sync_hatch_bar()

    def refresh_grid(self) -> None:
        self._rebuild_grid()
        self._refresh_currency_pills()

    def refresh_locale(self) -> None:
        if self._scroll is None:
            return
        old = self._scroll.takeWidget()
        if old is not None:
            old.deleteLater()
        body = QWidget()
        body.setStyleSheet("background: transparent;")
        sel = self._selection
        self._tiles = populate_collection_body(
            body,
            entries=self._entry_builder(self.session.player),
            empty_hint=self._empty_hint,
            grid_gap=self._grid_gap,
            grid_h_gap=self._grid_h_gap,
            grid_v_gap=self._grid_v_gap,
            grid_margin_h=self._margin_h,
            on_select=self._on_tile_selected,
            selected=sel,
        )
        self._scroll.setWidget(body)
        self._refresh_hatch_slots()
        self._refresh_currency_pills()
