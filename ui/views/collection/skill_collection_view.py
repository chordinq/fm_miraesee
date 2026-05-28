# ui/views/collection/skill_collection_div.py — skill tab with summon footer in panel
from __future__ import annotations

from core.enums import CurrencyType
from ui.views.collection.collection_screen_view import CollectionScreenView
from ui.views.collection.footer_placement import FooterPlacement
from ui.services.collection_entries import skill_entries
from features.session import Session
from ui.theme.metrics import (
    FRAMED_GRID_H_GAP,
    FRAMED_GRID_MARGIN_H,
    FRAMED_GRID_V_GAP,
)
from ui.widgets.skill_summon_bar import SkillSummonBar


class SkillCollectionView(CollectionScreenView):
    def __init__(self, session: Session, parent=None) -> None:
        self._summon_bar = SkillSummonBar(session)
        self._summon_bar.summon_finished.connect(self._on_summon_finished)
        super().__init__(
            session,
            entry_builder=skill_entries,
            empty_hint="No skills in dump.",
            grid_h_gap=FRAMED_GRID_H_GAP,
            grid_v_gap=FRAMED_GRID_V_GAP,
            grid_margin_h=FRAMED_GRID_MARGIN_H,
            footer=self._summon_bar,
            footer_placement=FooterPlacement.IN_PANEL,
            currency_left=CurrencyType.SkillSummonTickets,
            parent=parent,
        )

    def _on_summon_finished(self) -> None:
        self.refresh_grid()
        self._summon_bar.refresh()

    def refresh_locale(self) -> None:
        super().refresh_locale()
        self._summon_bar.refresh()
