# ui/widgets/currency_pill_widget.py — icon + dark pill bar (Image2 layout)
from __future__ import annotations

from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPen,
    QPixmap,
)
from PySide6.QtWidgets import QSizePolicy, QWidget

from core.enums import CurrencyType
from core.game_logic.player_model.PlayerModel import PlayerModel
from ui.services.currency_display import format_currency_amount
from ui.services.icon_sprites import currency_icon_pixmap
from ui.services.pixmap_util import default_device_pixel_ratio, draw_pixmap_in_rect
from ui.services.sprite import SpriteSpec, composite
from ui.theme.fonts import paint_ui_text, ui_text_style
from ui.theme.metrics import (
    CURRENCY_PILL_BAR_FILL,
    CURRENCY_PILL_BAR_H,
    CURRENCY_PILL_BAR_W,
    CURRENCY_PILL_BAR_X,
    CURRENCY_PILL_FONT_REF,
    CURRENCY_PILL_ICON,
    CURRENCY_PILL_ICON_CENTER_X,
    CURRENCY_PILL_ICON_CENTER_Y,
    CURRENCY_PILL_OUTLINE,
    CURRENCY_PILL_REF_H,
    CURRENCY_PILL_TEXT_PAD_RIGHT,
    CURRENCY_PILL_UNIT_PX,
    currency_pill_pixel_size,
    currency_pill_ref_width,
    currency_pill_scale,
)

_PILL_TEXTURE = "Rect_Extra_Rounded_Filled_Outline.png"


class CurrencyPillWidget(QWidget):
    """
    Ref layout 14×4: 4×4 icon centered at (2,2), bar 12×2.25 from x=2, outline 0.25 black.
    Background pill bar is drawn using the Rect_Extra_Rounded_Filled_Outline texture.
    """

    def __init__(
        self,
        player: PlayerModel,
        currency: CurrencyType,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._currency = currency
        self._amount = 0
        self._icon_pixmap: QPixmap | None = None
        self._pill_pixmap: QPixmap | None = None
        self._apply_pixel_size()
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.refresh()

    def _u(self, value: float) -> float:
        return value * currency_pill_scale()

    def _apply_pixel_size(self) -> None:
        pw, ph = currency_pill_pixel_size()
        self.setFixedSize(pw, ph)
        self._rebuild_pill_pixmap()

    def _rebuild_pill_pixmap(self) -> None:
        u = currency_pill_scale()
        bar_w = max(1, round(CURRENCY_PILL_BAR_W * u))
        bar_h = max(1, round(CURRENCY_PILL_BAR_H * u))
        self._pill_pixmap = composite(
            SpriteSpec(_PILL_TEXTURE, bar_w, bar_h, color=CURRENCY_PILL_BAR_FILL),
        )

    def refresh(self) -> None:
        self._amount = int(self._player.get_currency(self._currency))
        dpr = self.devicePixelRatioF()
        if dpr <= 0:
            dpr = default_device_pixel_ratio()
        icon_logical = round(CURRENCY_PILL_ICON * CURRENCY_PILL_UNIT_PX)
        self._icon_pixmap = currency_icon_pixmap(
            self._currency,
            icon_logical,
            device_pixel_ratio=dpr,
        )
        self.update()

    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        u = currency_pill_scale()
        bar_x = CURRENCY_PILL_BAR_X * u
        bar_w = CURRENCY_PILL_BAR_W * u
        bar_h = CURRENCY_PILL_BAR_H * u
        bar_y = (CURRENCY_PILL_REF_H * u - bar_h) / 2.0

        # --- Background pill (texture-based) ---
        if self._pill_pixmap is not None and not self._pill_pixmap.isNull():
            draw_pixmap_in_rect(
                painter,
                QRectF(bar_x, bar_y, bar_w, bar_h),
                self._pill_pixmap,
            )
        else:
            # Fallback: direct QPainterPath draw if texture unavailable
            outline = CURRENCY_PILL_OUTLINE * u
            radius = max(1.0, bar_h * 0.45)
            bar_rect = QRectF(bar_x, bar_y, bar_w, bar_h)
            path = QPainterPath()
            path.addRoundedRect(bar_rect, radius, radius)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(CURRENCY_PILL_BAR_FILL))
            painter.drawPath(path)
            stroke_pen = QPen(QColor("#000000"), outline)
            stroke_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
            stroke_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(stroke_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)

        # --- Currency icon ---
        if self._icon_pixmap is not None and not self._icon_pixmap.isNull():
            icon_side = CURRENCY_PILL_ICON * u
            cx = CURRENCY_PILL_ICON_CENTER_X * u
            cy = CURRENCY_PILL_ICON_CENTER_Y * u
            ix = cx - icon_side / 2.0
            iy = cy - icon_side / 2.0
            target = QRectF(ix, iy, icon_side, icon_side)
            draw_pixmap_in_rect(painter, target, self._icon_pixmap)

        # --- Amount text ---
        text = format_currency_amount(self._amount)
        pill_font_size = max(8, round(CURRENCY_PILL_FONT_REF * CURRENCY_PILL_UNIT_PX * 0.72))
        stroke_w = max(1.0, CURRENCY_PILL_OUTLINE * u * 0.85)
        text_style = ui_text_style(pill_font_size, stroke_w)
        metrics = QFontMetrics(text_style.font())
        pad_r = metrics.horizontalAdvance(" ") + CURRENCY_PILL_TEXT_PAD_RIGHT * u
        text_x = bar_x + bar_w - pad_r - metrics.horizontalAdvance(text)
        text_left = bar_x + CURRENCY_PILL_ICON * u * 0.55
        text_rect = QRectF(text_left, bar_y, bar_x + bar_w - text_left, bar_h)
        baseline = text_rect.center().y() + (metrics.ascent() - metrics.descent()) / 2.0
        paint_ui_text(painter, text, text_x, baseline, text_style)
