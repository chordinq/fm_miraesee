# ui/views/collection/mount_collection_div.py
from __future__ import annotations

from core.enums import CurrencyType
from ui.views.collection.collection_screen_view import CollectionScreenView
from ui.services.collection_entries import mount_entries
from features.session import Session
from ui.theme.metrics import (
    FRAMED_GRID_H_GAP,
    FRAMED_GRID_MARGIN_H,
    FRAMED_GRID_V_GAP,
)


class MountCollectionView(CollectionScreenView):
    def __init__(self, session: Session, parent=None) -> None:
        super().__init__(
            session,
            entry_builder=mount_entries,
            empty_hint="No mounts in dump.",
            grid_h_gap=FRAMED_GRID_H_GAP,
            grid_v_gap=FRAMED_GRID_V_GAP,
            grid_margin_h=FRAMED_GRID_MARGIN_H,
            currency_left=CurrencyType.ClockWinders,
            parent=parent,
        )
