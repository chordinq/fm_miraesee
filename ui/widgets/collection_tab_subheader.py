# ui/widgets/collection_tab_subheader.py — currency (left) + equipped strip (right)
from __future__ import annotations

from typing import Literal

from PySide6.QtCore import Qt, QRectF, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QHBoxLayout, QSizePolicy, QWidget

from core.enums import CurrencyType
from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.theme.colors import COLLECTION_SUBHEADER_BG
from ui.theme.metrics import PET_SUBHEADER_HEIGHT
from ui.services.collection_selection import CollectionSelection
from ui.widgets.currency_strip import CurrencyStrip
from ui.widgets.equipped_collection_bar import EquippedCollectionBar, EquippedKind

EquippedKindOpt = EquippedKind | None


class CollectionTabSubHeader(QWidget):
    """Dark bar: tab currency left, equipped items right."""

    item_selected = Signal(object)

    def __init__(
        self,
        player: PlayerModel,
        currency: CurrencyType,
        *,
        equipped_kind: EquippedKindOpt = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._equipped_kind = equipped_kind
        self.setObjectName("CollectionTabSubHeader")
        self.setFixedHeight(PET_SUBHEADER_HEIGHT)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(12, 5, 12, 5)
        outer.setSpacing(12)

        self._currency = CurrencyStrip(player, currency, self)
        outer.addWidget(self._currency, 1)

        self._equipped: EquippedCollectionBar | None = None
        if equipped_kind is not None:
            self._equipped = EquippedCollectionBar(
                player, equipped_kind, embedded=True, parent=self
            )
            self._equipped.item_selected.connect(self.item_selected.emit)
            outer.addWidget(
                self._equipped,
                0,
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter,
            )

    def set_selection(self, selection: CollectionSelection | None) -> None:
        if self._equipped is not None:
            self._equipped.set_selection(selection)

    def refresh(self) -> None:
        self._currency.refresh()
        if self._equipped is not None:
            self._equipped.refresh()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QColor(COLLECTION_SUBHEADER_BG))
        painter.drawRoundedRect(QRectF(0, 0, self.width(), self.height()), 8, 8)
