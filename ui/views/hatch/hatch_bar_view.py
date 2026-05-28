# ui/views/hatch/hatch_bar_div.py — hatch footer region (layout + metrics only)
from __future__ import annotations

from dataclasses import dataclass

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from ui.theme.colors import HATCH_BAR_BG
from ui.theme.metrics import FRAMED_GRID_MARGIN_H
from ui.theme.metrics import (
    HATCH_BAR_MIN_HEIGHT,
    HatchBarMetrics,
    hatch_bar_horizontal_margins,
    hatch_bar_metrics,
)
from ui.widgets.hatch.hatch_slot_row import HatchSlotRowWidget


@dataclass(frozen=True)
class HatchBarSpec:
    metrics: HatchBarMetrics

    @property
    def bar_height(self) -> int:
        return self.metrics.bar_height


def compute_hatch_bar_spec(
    panel_width: int,
    *,
    grid_margin_h: int = FRAMED_GRID_MARGIN_H,
) -> HatchBarSpec:
    return HatchBarSpec(
        metrics=hatch_bar_metrics(panel_width, grid_margin_h=grid_margin_h),
    )


class HatchBarView(QWidget):
    """Dark hatch strip inside collection panel; owns size, centers slot row."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("HatchBarRegion")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        self.setStyleSheet(
            f"QWidget#HatchBarRegion {{ background-color: {HATCH_BAR_BG}; border: none; }}"
        )
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(HATCH_BAR_BG))
        self.setPalette(palette)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setMinimumHeight(HATCH_BAR_MIN_HEIGHT)

        self._spec: HatchBarSpec | None = None
        self._row = HatchSlotRowWidget(self)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addStretch(1)
        outer.addWidget(self._row, 0, Qt.AlignmentFlag.AlignHCenter)
        outer.addStretch(1)

    @property
    def row(self) -> HatchSlotRowWidget:
        return self._row

    def apply_spec(
        self,
        spec: HatchBarSpec,
        *,
        grid_margin_h: int = FRAMED_GRID_MARGIN_H,
    ) -> None:
        self._spec = spec
        m = spec.metrics
        self.setFixedHeight(spec.bar_height)
        layout = self.layout()
        if layout is not None:
            margin_l, margin_r = hatch_bar_horizontal_margins(
                grid_margin_h=grid_margin_h,
            )
            layout.setContentsMargins(margin_l, m.pad_v, margin_r, m.pad_v)
        self._row.apply_metrics(m)

    def sync_panel_width(
        self,
        panel_width: int,
        *,
        grid_margin_h: int = FRAMED_GRID_MARGIN_H,
    ) -> None:
        self.apply_spec(
            compute_hatch_bar_spec(panel_width, grid_margin_h=grid_margin_h),
            grid_margin_h=grid_margin_h,
        )
