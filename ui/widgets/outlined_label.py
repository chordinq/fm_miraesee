# ui/widgets/outlined_label.py — text with separate fill + outline (QPainter)
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QFont,
    QFontMetrics,
    QPainter,
    QPaintEvent,
)
from PySide6.QtWidgets import QLabel, QSizePolicy

from ui.theme.fonts import (
    OUTLINE_FILL,
    TEXT_STYLE_COLLECTION,
    TEXT_STYLE_TITLE,
    UiTextStyle,
    paint_ui_text,
    ui_text_style,
)

_DETAIL_TITLE_STYLE = ui_text_style(15, 2, outline_mode="stroker")
from ui.theme.metrics import CURRENCY_STRIP_FONT_SIZE, CURRENCY_STRIP_ROW_H


def currency_amount_label(text: str = "", parent=None) -> "OutlinedLabel":
    """Outlined balance next to currency icon in collection sub-header."""
    style = ui_text_style(CURRENCY_STRIP_FONT_SIZE, 3)
    label = OutlinedLabel(text, parent, style=style)
    label.setFixedHeight(CURRENCY_STRIP_ROW_H)
    return label


def tile_caption_label(text: str = "", parent=None) -> "OutlinedLabel":
    """Outlined caption under collection icons (Lv. / 알 / Egg / 卵 — same style)."""
    return OutlinedLabel(text, parent, style=TEXT_STYLE_COLLECTION)


def collection_caption_label(
    text: str = "",
    parent=None,
    *,
    point_size: int | None = None,
    outline_width: float | None = None,
    bold: bool = True,
    fill: str = OUTLINE_FILL,
) -> "OutlinedLabel":
    """Alias for tile_caption_label with optional overrides."""
    style = TEXT_STYLE_COLLECTION
    if point_size is not None or outline_width is not None:
        style = ui_text_style(
            point_size if point_size is not None else style.point_size,
            outline_width if outline_width is not None else style.outline_width,
            bold=bold,
            fill=fill,
        )
    return OutlinedLabel(text, parent, style=style)


# Back-compat alias
level_caption_label = tile_caption_label


def detail_title_label(text: str = "", parent=None) -> "OutlinedLabel":
    """Detail panel title ([Epic] Tiger) — left-aligned, black outline + rarity fill."""
    label = OutlinedLabel(text, parent, style=_DETAIL_TITLE_STYLE)
    label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
    label.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
    return label


class OutlinedLabel(QLabel):
    """Game-style label: vector stroke behind fill.

    Uses an internal paint font because the app global QSS (* { font-size: Npx })
    overrides QLabel.font() and would ignore setPointSize().
    """

    def __init__(
        self,
        text: str = "",
        parent=None,
        *,
        style: UiTextStyle | None = None,
        fill: str | None = None,
        stroke: str | None = None,
        stroke_width: int | float | None = None,
        point_size: int | None = None,
        bold: bool = True,
        outline_mode: str = "pen",
    ) -> None:
        super().__init__(text, parent)
        if style is None:
            style = ui_text_style(
                point_size if point_size is not None else TEXT_STYLE_TITLE.point_size,
                stroke_width if stroke_width is not None else TEXT_STYLE_TITLE.outline_width,
                bold=bold,
                fill=fill if fill is not None else OUTLINE_FILL,
                stroke=stroke if stroke is not None else TEXT_STYLE_TITLE.stroke,
                outline_mode=outline_mode if outline_mode in ("pen", "stroker") else "pen",  # type: ignore[arg-type]
            )
        self._style = style
        self._paint_font = style.font()
        super().setFont(self._paint_font)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("color: transparent; background: transparent; border: none;")
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self._sync_dimensions()

    @property
    def text_style(self) -> UiTextStyle:
        return self._style

    def font(self) -> QFont:  # noqa: D102
        return QFont(self._paint_font)

    def point_size(self) -> int:
        return self._style.point_size

    def set_text_style(self, style: UiTextStyle) -> None:
        self._style = style
        self._rebuild_paint_font()

    def set_point_size(self, point_size: int, *, bold: bool | None = None) -> None:
        self._style = ui_text_style(
            point_size,
            self._style.outline_width,
            bold=self._style.bold if bold is None else bold,
            fill=self._style.fill,
            stroke=self._style.stroke,
            outline_mode=self._style.outline_mode,
        )
        self._rebuild_paint_font()

    def _rebuild_paint_font(self) -> None:
        self._paint_font = self._style.font()
        super().setFont(self._paint_font)
        self._sync_dimensions()
        self.update()

    def _outline_pad(self) -> int:
        return self._style.outline_pad()

    def _text_baseline(self, metrics: QFontMetrics, rect) -> tuple[float, float]:
        text = self.text()
        tw = metrics.horizontalAdvance(text)
        th = metrics.ascent() + metrics.descent()
        align = self.alignment()
        x = float(rect.x())
        y = float(rect.y())
        if align & Qt.AlignmentFlag.AlignHCenter:
            x += (rect.width() - tw) / 2.0
        elif align & Qt.AlignmentFlag.AlignRight:
            x += rect.width() - tw
        if align & Qt.AlignmentFlag.AlignVCenter:
            y += (rect.height() - th) / 2.0
        elif align & Qt.AlignmentFlag.AlignBottom:
            y += rect.height() - th
        return x, y + metrics.ascent()

    def caption_height(self) -> int:
        metrics = QFontMetrics(self._paint_font)
        return metrics.height() + 2 * self._outline_pad()

    def caption_width(self) -> int:
        metrics = QFontMetrics(self._paint_font)
        text = self.text() or " "
        return metrics.horizontalAdvance(text) + 2 * self._outline_pad()

    def _sync_dimensions(self) -> None:
        self.setFixedSize(self.caption_width(), self.caption_height())

    def set_fill_color(self, color: str) -> None:
        self._style = ui_text_style(
            self._style.point_size,
            self._style.outline_width,
            bold=self._style.bold,
            fill=color,
            stroke=self._style.stroke,
            outline_mode=self._style.outline_mode,
        )
        self.update()

    def setText(self, text: str) -> None:  # noqa: N802
        super().setText(text)
        self._sync_dimensions()
        self.update()

    def setFont(self, font: QFont) -> None:  # noqa: N802
        self._paint_font = QFont(font)
        self._style = ui_text_style(
            font.pointSize() if font.pointSize() > 0 else self._style.point_size,
            self._style.outline_width,
            bold=font.bold(),
            fill=self._style.fill,
            stroke=self._style.stroke,
            outline_mode=self._style.outline_mode,
        )
        super().setFont(font)
        self._sync_dimensions()
        self.update()

    def paintEvent(self, event: QPaintEvent) -> None:  # noqa: N802
        text = self.text()
        if not text:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)

        font = self._paint_font
        metrics = QFontMetrics(font)
        pad = self._outline_pad()
        rect = self.contentsRect().adjusted(pad, pad, -pad, -pad)
        x, baseline = self._text_baseline(metrics, rect)

        paint_ui_text(painter, text, x, baseline, self._style, font=font)
