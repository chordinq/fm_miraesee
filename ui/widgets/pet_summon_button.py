# ui/widgets/pet_summon_button.py — 9-slice summon button with title + eggshell cost
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QFontMetrics, QPainter, QPixmap
from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.services.currency_display import format_currency_amount
from ui.services.icon_sprites import currency_icon_pixmap
from ui.services.pet_summon import (
    can_afford_pet_summon,
    pet_summon_cost,
    pet_summon_currency,
    pet_summon_title,
)
from ui.services.pixmap_util import default_device_pixel_ratio
from ui.theme.fonts import paint_ui_text, ui_text_style

_TITLE_STYLE = ui_text_style(14, 3)
_COST_STYLE = ui_text_style(12, 3)
from ui.theme.metrics import (
    PET_SUMMON_BUTTON_COLOR,
    PET_SUMMON_COST_GAP,
    PET_SUMMON_COST_ICON,
    PET_SUMMON_COST_X,
    PET_SUMMON_COST_Y,
    PET_SUMMON_TITLE_Y_RATIO,
)
from ui.widgets.slice_button import SliceButton


class PetSummonButton(SliceButton):
    def __init__(
        self,
        player: PlayerModel,
        *,
        logical_w: int,
        logical_h: int,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(
            logical_w=logical_w,
            logical_h=logical_h,
            color_hex=PET_SUMMON_BUTTON_COLOR,
            parent=parent,
        )
        self._player = player
        self._title_style = _TITLE_STYLE
        self._cost_style = _COST_STYLE
        self._title_text = ""
        self._cost_text = ""
        self._cost_icon: QPixmap | None = None
        self.refresh()

    def refresh(self) -> None:
        self._title_text = pet_summon_title()
        self._cost_text = format_currency_amount(pet_summon_cost(self._player))
        dpr = self.devicePixelRatioF()
        if dpr <= 0:
            dpr = default_device_pixel_ratio()
        self._cost_icon = currency_icon_pixmap(
            pet_summon_currency(),
            PET_SUMMON_COST_ICON,
            device_pixel_ratio=dpr,
        )
        self.setEnabled(can_afford_pet_summon(self._player))
        self.update()

    def paintEvent(self, event) -> None:  # noqa: N802
        super().paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setClipRect(self.rect())
        self._paint_cost(painter)
        self._paint_title(painter)
        painter.end()

    def _paint_cost(self, painter: QPainter) -> None:
        x = PET_SUMMON_COST_X
        y = PET_SUMMON_COST_Y
        if self._cost_icon is not None and not self._cost_icon.isNull():
            painter.drawPixmap(
                x,
                y,
                PET_SUMMON_COST_ICON,
                PET_SUMMON_COST_ICON,
                self._cost_icon,
            )
            x += PET_SUMMON_COST_ICON + PET_SUMMON_COST_GAP
        if self._cost_text:
            metrics = QFontMetrics(self._cost_style.font())
            baseline = y + (PET_SUMMON_COST_ICON + metrics.ascent() - metrics.descent()) // 2
            max_cost_w = self.width() // 2 - PET_SUMMON_COST_X
            cost_display = self._cost_text
            while (
                len(cost_display) > 1
                and metrics.horizontalAdvance(cost_display) > max_cost_w
            ):
                cost_display = cost_display[:-1]
            paint_ui_text(
                painter,
                cost_display,
                float(x),
                float(baseline),
                self._cost_style,
            )

    def _paint_title(self, painter: QPainter) -> None:
        if not self._title_text:
            return
        metrics = QFontMetrics(self._title_style.font())
        tw = metrics.horizontalAdvance(self._title_text)
        x = (self.width() - tw) // 2
        y = int(self.height() * PET_SUMMON_TITLE_Y_RATIO)
        baseline = y + (metrics.ascent() - metrics.descent()) // 2
        paint_ui_text(
            painter,
            self._title_text,
            float(x),
            float(baseline),
            self._title_style,
        )
