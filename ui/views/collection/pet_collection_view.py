# ui/views/collection/pet_collection_div.py — pet tab with hatch + summon footers
from __future__ import annotations

from core.enums import CurrencyType
from ui.views.collection.collection_footer_stack import stack_panel_footers
from ui.views.collection.collection_screen_view import CollectionScreenView
from ui.views.collection.footer_placement import FooterPlacement
from ui.views.hatch.hatch_bar_view import HatchBarView
from ui.views.summon.pet_summon_bar_view import PetSummonBarView
from ui.services.collection_entries import pet_entries
from features.session import Session
from ui.theme.metrics import (
    FRAMED_GRID_H_GAP,
    FRAMED_GRID_MARGIN_H,
    FRAMED_GRID_V_GAP,
)


class PetCollectionView(CollectionScreenView):
    def __init__(self, session: Session, parent=None) -> None:
        self._hatch_footer = HatchBarView()
        self._summon_footer = PetSummonBarView(session)
        self._summon_footer.summon_finished.connect(self._on_summon_finished)
        footer = stack_panel_footers(self._hatch_footer, self._summon_footer)
        super().__init__(
            session,
            entry_builder=pet_entries,
            empty_hint="No pets or eggs in dump.",
            grid_h_gap=FRAMED_GRID_H_GAP,
            grid_v_gap=FRAMED_GRID_V_GAP,
            grid_margin_h=FRAMED_GRID_MARGIN_H,
            grid_margin_bottom=FRAMED_GRID_V_GAP + 4,
            footer=footer,
            footer_placement=FooterPlacement.IN_PANEL,
            currency_left=CurrencyType.Eggshells,
            currency_right=CurrencyType.Gems,
            parent=parent,
        )

    def _on_summon_finished(self) -> None:
        self.refresh_grid()

    def _sync_hatch_bar(self) -> None:
        super()._sync_hatch_bar()

    def refresh_grid(self) -> None:
        super().refresh_grid()
        self._summon_footer.refresh()
