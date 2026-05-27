# ui/widgets/hatch_slot_bar.py — fixed 4-slot hatch incubator (full-width bottom bar)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPainter, QPalette, QPaintEvent
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from core.game_logic.player_model.EggModel import EggModel
from ui.constants.colors import HATCH_BAR_BG
from ui.constants.layout import (
    HATCH_BAR_HEIGHT,
    HATCH_SCENE_H,
    HATCH_SCENE_W,
    HATCH_SLOT_COUNT,
    HATCH_SLOT_GAP,
)
from ui.services.hatch_layout import HatchLayer, build_hatch_layers


def _transparent_label(parent: QWidget) -> QLabel:
    label = QLabel(parent)
    label.setStyleSheet("background: transparent;")
    return label


def _place_layer(label: QLabel, layer: HatchLayer) -> None:
    label.setPixmap(layer.pixmap)
    label.setFixedSize(layer.pixmap.size())
    label.move(layer.x, layer.y)
    label.show()


class _HatchSlotScene(QWidget):
    def __init__(self, egg: EggModel | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(HATCH_SCENE_W, HATCH_SCENE_H)
        self.setStyleSheet("background: transparent;")

        for layer in build_hatch_layers(egg):
            label = _transparent_label(self)
            _place_layer(label, layer)


class _HatchSlotCell(QWidget):
    def __init__(self, egg: EggModel | None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setFixedSize(HATCH_SCENE_W, HATCH_SCENE_H)
        self.setStyleSheet("background: transparent;")
        _HatchSlotScene(egg, self)


def _hatch_slots_row_width() -> int:
    return HATCH_SLOT_COUNT * HATCH_SCENE_W + (HATCH_SLOT_COUNT - 1) * HATCH_SLOT_GAP


class HatchSlotBar(QWidget):
    """Full-width dark hatch bar at the bottom of the collection column."""

    def __init__(
        self,
        slots: list[EggModel | None],
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setObjectName("HatchSlotBar")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setAutoFillBackground(True)
        pal = self.palette()
        pal.setColor(QPalette.ColorRole.Window, QColor(HATCH_BAR_BG))
        self.setPalette(pal)
        self.setFixedHeight(HATCH_BAR_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setStyleSheet(f"QWidget#HatchSlotBar {{ background-color: {HATCH_BAR_BG}; }}")

        row_host = QWidget()
        row_host.setFixedSize(_hatch_slots_row_width(), HATCH_SCENE_H)
        row_host.setStyleSheet("background: transparent;")
        row = QHBoxLayout(row_host)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(HATCH_SLOT_GAP)
        for i in range(HATCH_SLOT_COUNT):
            egg = slots[i] if i < len(slots) else None
            row.addWidget(_HatchSlotCell(egg))

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 4, 0, 4)
        outer.addStretch(1)
        outer.addWidget(row_host, 0, Qt.AlignmentFlag.AlignVCenter)
        outer.addStretch(1)

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(HATCH_BAR_BG))
        super().paintEvent(event)
