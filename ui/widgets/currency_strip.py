# ui/widgets/currency_strip.py — icon + balance for wallet currencies
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QHBoxLayout, QLabel, QSizePolicy, QWidget

from core.enums import CurrencyType
from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.theme.metrics import (
    CURRENCY_STRIP_CHIP_GAP,
    CURRENCY_STRIP_ICON,
    CURRENCY_STRIP_ROW_H,
)
from ui.services.currency_display import format_currency_amount, tab_currency_row
from ui.services.icon_sprites import currency_icon_pixmap
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.widgets.outlined_label import currency_amount_label


def _pixmap_logical_size(pixmap: QPixmap) -> tuple[int, int]:
    dpr = pixmap.devicePixelRatio()
    if dpr > 1.0:
        return max(1, round(pixmap.width() / dpr)), max(1, round(pixmap.height() / dpr))
    return pixmap.width(), pixmap.height()


class _CurrencyChip(QWidget):
    def __init__(
        self,
        currency: CurrencyType,
        amount: int,
        *,
        device_pixel_ratio: float,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        self.setFixedHeight(CURRENCY_STRIP_ROW_H)
        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(CURRENCY_STRIP_CHIP_GAP)
        row.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        icon_lbl = QLabel()
        icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_lbl.setStyleSheet("background: transparent;")
        pix = currency_icon_pixmap(
            currency,
            CURRENCY_STRIP_ICON,
            device_pixel_ratio=device_pixel_ratio,
        )
        if pix is not None and not pix.isNull():
            lw, lh = _pixmap_logical_size(pix)
            icon_lbl.setPixmap(pix)
            icon_lbl.setFixedSize(lw, lh)
        else:
            icon_lbl.setFixedSize(CURRENCY_STRIP_ICON, CURRENCY_STRIP_ICON)
        row.addWidget(icon_lbl, 0, Qt.AlignmentFlag.AlignVCenter)

        amt_lbl = currency_amount_label(format_currency_amount(amount))
        row.addWidget(amt_lbl, 0, Qt.AlignmentFlag.AlignVCenter)


class CurrencyStrip(QWidget):
    """Single currency icon + balance (collection tab sub-header)."""

    def __init__(
        self,
        player: PlayerModel,
        currency: CurrencyType,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._currency = currency
        self.setObjectName("CurrencyStrip")
        self.setStyleSheet("background: transparent;")
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(CURRENCY_STRIP_ROW_H)

        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(14)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.refresh()

    def _device_pixel_ratio(self) -> float:
        dpr = self.devicePixelRatioF()
        return dpr if dpr > 0 else default_device_pixel_ratio()

    def refresh(self) -> None:
        while self._layout.count():
            item = self._layout.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()

        dpr = self._device_pixel_ratio()
        for ctype, amount in tab_currency_row(self._player, self._currency):
            self._layout.addWidget(
                _CurrencyChip(ctype, amount, device_pixel_ratio=dpr, parent=self),
            )
