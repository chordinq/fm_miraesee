# ui/views/skill_view.py
from __future__ import annotations

from ui.constants.layout import FRAMED_GRID_H_GAP, FRAMED_GRID_MARGIN_H, FRAMED_GRID_V_GAP
from ui.services.collection_entries import skill_entries
from ui.services.session import Session
from ui.views.collection_view import CollectionView


class SkillView(CollectionView):
    def __init__(self, session: Session, parent=None) -> None:
        super().__init__(
            session,
            entry_builder=skill_entries,
            empty_hint="No skills in dump.",
            grid_h_gap=FRAMED_GRID_H_GAP,
            grid_v_gap=FRAMED_GRID_V_GAP,
            grid_margin_h=FRAMED_GRID_MARGIN_H,
            parent=parent,
        )
