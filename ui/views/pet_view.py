# ui/views/pet_view.py
from __future__ import annotations

from ui.constants.layout import (
    FRAMED_GRID_H_GAP,
    FRAMED_GRID_MARGIN_H,
    FRAMED_GRID_V_GAP,
)
from ui.services.collection_entries import pet_entries
from ui.services.session import Session
from ui.views.collection_view import CollectionView
from ui.widgets.hatch_slot_bar import HatchSlotBar


class PetView(CollectionView):
    def __init__(self, session: Session, parent=None) -> None:
        hatch_bar = HatchSlotBar(session.player.pets.hatch_slots())
        super().__init__(
            session,
            entry_builder=pet_entries,
            empty_hint="No pets or eggs in dump.",
            grid_h_gap=FRAMED_GRID_H_GAP,
            grid_v_gap=FRAMED_GRID_V_GAP,
            grid_margin_h=FRAMED_GRID_MARGIN_H,
            bottom_widget=hatch_bar,
            parent=parent,
        )
