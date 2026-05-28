# ui/widgets/hatch/hatch_slot_row.py — row of 4 hatch slots (assembly + selection signals)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from core.game_logic.player_model.EggModel import EggModel
from ui.services.collection_selection import CollectionSelection
from ui.theme.metrics import HATCH_SLOT_COUNT, HatchBarMetrics
from ui.widgets.hatch.hatch_slot_widget import HatchSlotWidget


class HatchSlotRowWidget(QWidget):
    """Four hatch slots; dimensions come from HatchBarMetrics (div-owned)."""

    slot_clicked = Signal(object)  # CollectionSelection

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self._metrics: HatchBarMetrics | None = None
        self._cells: list[HatchSlotWidget] = []
        self._last_slots: list[EggModel | None] = []

        self._row = QHBoxLayout(self)
        self._row.setContentsMargins(0, 0, 0, 0)
        self._row.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def apply_metrics(self, metrics: HatchBarMetrics) -> None:
        if (
            self._metrics is not None
            and self._metrics.scene_w == metrics.scene_w
            and self._metrics.scene_h == metrics.scene_h
            and self._metrics.slot_gap == metrics.slot_gap
            and self._cells
        ):
            self._metrics = metrics
            self.setFixedSize(metrics.row_width, metrics.scene_h)
            return
        self._metrics = metrics
        self._row.setSpacing(metrics.slot_gap)
        self._rebuild_cells(metrics)
        if self._last_slots:
            self.set_slots(self._last_slots)

    def _rebuild_cells(self, metrics: HatchBarMetrics) -> None:
        while self._row.count():
            item = self._row.takeAt(0)
            if item.widget() is not None:
                item.widget().deleteLater()
        self._cells.clear()
        self.setFixedSize(metrics.row_width, metrics.scene_h)
        for _ in range(HATCH_SLOT_COUNT):
            cell = HatchSlotWidget(
                None,
                scene_w=metrics.scene_w,
                scene_h=metrics.scene_h,
            )
            self._cells.append(cell)
            self._row.addWidget(cell)
        self._wire_cells()

    def set_slots(self, slots: list[EggModel | None]) -> None:
        self._last_slots = list(slots)
        if self._metrics is None:
            return
        m = self._metrics
        for i, cell in enumerate(self._cells):
            egg = slots[i] if i < len(slots) else None
            cell.set_egg(egg)
            cell.apply_size(m.scene_w, m.scene_h)
        self._wire_cells()

    def set_selected(self, selection: CollectionSelection | None) -> None:
        for cell in self._cells:
            if (
                selection is not None
                and selection.kind == "egg"
                and cell.egg is selection.egg
            ):
                cell.set_selected(True)
            else:
                cell.set_selected(False)

    def _wire_cells(self) -> None:
        for cell in self._cells:
            try:
                cell.clicked.disconnect()
            except RuntimeError:
                pass
            if cell.egg is not None:
                sel = cell.selection
                cell.clicked.connect(
                    lambda _checked=False, s=sel: self.slot_clicked.emit(s)
                )
