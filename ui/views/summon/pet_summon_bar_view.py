# ui/views/summon/pet_summon_bar_div.py — summon strip below hatch bar
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from features.session import Session
from features.summon.pet_summon import execute_pet_summon
from ui.theme.colors import COLLECTION_BG
from ui.theme.metrics import collection_panel_width
from ui.theme.metrics import (
    PET_SUMMON_BAR_HEIGHT,
    PET_SUMMON_BAR_PAD_H,
    PET_SUMMON_BAR_PAD_V,
    PET_SUMMON_BUTTON_H,
    PET_SUMMON_BUTTON_MAX_W,
    PET_SUMMON_BUTTON_MIN_W,
)
from ui.services.button0_texture import button0_fitted_size
from ui.widgets.pet_summon_button import PetSummonButton


class PetSummonBarView(QWidget):
    summon_finished = Signal()

    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._session = session
        self.setObjectName("PetSummonBar")
        self.setFixedHeight(PET_SUMMON_BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"QWidget#PetSummonBar {{ background-color: {COLLECTION_BG}; }}")

        fw, fh = button0_fitted_size(
            PET_SUMMON_BUTTON_MIN_W,
            PET_SUMMON_BUTTON_H,
        )
        self._button = PetSummonButton(
            session.player,
            logical_w=fw,
            logical_h=fh,
            parent=self,
        )
        self._button.clicked.connect(self._on_summon)

        row = QHBoxLayout(self)
        row.setContentsMargins(
            PET_SUMMON_BAR_PAD_H,
            PET_SUMMON_BAR_PAD_V,
            PET_SUMMON_BAR_PAD_H,
            PET_SUMMON_BAR_PAD_V,
        )
        row.addStretch(1)
        row.addWidget(self._button, 0, Qt.AlignmentFlag.AlignCenter)
        row.addStretch(1)
        self.refresh()

    def sync_panel_width(self, panel_width: int) -> None:
        inner = max(1, panel_width - 2 * PET_SUMMON_BAR_PAD_H)
        slot_w = max(
            PET_SUMMON_BUTTON_MIN_W,
            min(PET_SUMMON_BUTTON_MAX_W, inner - 16),
        )
        fw, fh = button0_fitted_size(slot_w, PET_SUMMON_BUTTON_H)
        self._button.apply_logical_size(fw, fh)

    def refresh(self) -> None:
        self._button.refresh()

    def _on_summon(self) -> None:
        result = execute_pet_summon(self._session)
        if result.success:
            self.summon_finished.emit()
        self.refresh()
