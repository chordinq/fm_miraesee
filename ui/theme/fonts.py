# ui/theme/fonts.py — font constants and helpers (single source of truth)
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QFontMetrics,
    QPainter,
    QPainterPath,
    QPainterPathStroker,
    QPen,
)
from PySide6.QtWidgets import QApplication

from ui.services.locale import Language, locale_service

OutlineMode = Literal["pen", "stroker"]

# Fallback used before custom fonts are loaded, or if font files are missing
_FONT_FALLBACK = "Segoe UI"

# Populated by register_app_fonts(); maps font role → resolved Qt family name
_FONT_FAMILIES: dict[str, str] = {}

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
_FONT_DIR = _SCRIPTS_ROOT / "assets" / "Font"

_FONT_FILES: dict[str, str] = {
    "latin": "Baloo-Regular.ttf",
    "ko":    "NotoSansKR-Bold.otf",
    "ja":    "NotoSansJP-Bold.otf",
}

UI_FONT_SIZE = 13
UI_FONT_SIZE_TAB = 14
UI_FONT_SIZE_TITLE = 22
UI_FONT_SIZE_COLLECTION = 11
UI_FONT_SIZE_COLLECTION_SMALL = 8
UI_FONT_SIZE_EQUIPPED_BADGE = 8

# Text outline paint constants
OUTLINE_FILL = "#ffffff"
OUTLINE_STROKE = "#1a1a1a"
OUTLINE_STROKE_WIDTH = 2
COLLECTION_OUTLINE_STROKE = "#000000"
COLLECTION_OUTLINE_STROKE_WIDTH = 3


def register_app_fonts() -> None:
    """Load game font files into Qt's font database.

    Must be called after QApplication is created, before any widgets.
    Safe to call multiple times — skips files already loaded.
    """
    for role, filename in _FONT_FILES.items():
        path = _FONT_DIR / filename
        if not path.is_file():
            continue
        font_id = QFontDatabase.addApplicationFont(str(path))
        if font_id < 0:
            continue
        families = QFontDatabase.applicationFontFamilies(font_id)
        if families:
            _FONT_FAMILIES[role] = families[0]


def _latin_family() -> str:
    return _FONT_FAMILIES.get("latin", _FONT_FALLBACK)


def ui_font_families(language: Language | None = None) -> list[str]:
    """Return ordered font family list for the given language.

    Qt cascades through the list: the first family that contains a glyph is used.
    This means Baloo handles Latin/numbers, and the CJK font handles its script.
    """
    lang = language or locale_service.language
    latin = _latin_family()
    if lang == Language.KO:
        cjk = _FONT_FAMILIES.get("ko", _FONT_FALLBACK)
        return [latin, cjk, _FONT_FALLBACK, "sans-serif"]
    if lang == Language.JA:
        cjk = _FONT_FAMILIES.get("ja", _FONT_FALLBACK)
        return [latin, cjk, _FONT_FALLBACK, "sans-serif"]
    return [latin, _FONT_FALLBACK, "sans-serif"]


def ui_font_family_css(language: Language | None = None) -> str:
    return ", ".join(f'"{name}"' if " " in name else name for name in ui_font_families(language))


def build_app_font(*, point_size: int = UI_FONT_SIZE, bold: bool = False) -> QFont:
    font = QFont()
    font.setFamilies(ui_font_families())
    font.setPointSize(point_size)
    font.setBold(bold)
    return font


@dataclass(frozen=True)
class UiTextStyle:
    """Single spec for game UI text: size, optional outline, colors."""

    point_size: int
    outline_width: float = 0.0
    """Outline thickness in px; 0 draws fill only (no stroke)."""
    bold: bool = True
    fill: str = OUTLINE_FILL
    stroke: str = COLLECTION_OUTLINE_STROKE
    outline_mode: OutlineMode = "pen"

    def font(self, language: Language | None = None) -> QFont:
        _ = language
        return build_app_font(point_size=self.point_size, bold=self.bold)

    def has_outline(self) -> bool:
        return self.outline_width > 0

    def outline_pad(self) -> int:
        if not self.has_outline():
            return 0
        return int(self.outline_width) + 3


def ui_text_style(
    point_size: int,
    outline_width: float = 0,
    *,
    bold: bool = True,
    fill: str | None = None,
    stroke: str | None = None,
    outline_mode: OutlineMode = "pen",
) -> UiTextStyle:
    """Build a text style used by labels and QPainter text helpers.

    Examples:
        ui_text_style(13, 0)           # plain text, no outline
        ui_text_style(11, 3)           # collection caption (3px black outline)
        ui_text_style(14, 3).font()    # QFont for widgets
    """
    return UiTextStyle(
        point_size=point_size,
        outline_width=max(0.0, float(outline_width)),
        bold=bold,
        fill=fill if fill is not None else OUTLINE_FILL,
        stroke=stroke if stroke is not None else COLLECTION_OUTLINE_STROKE,
        outline_mode=outline_mode,
    )


# Named presets — prefer these over raw point_size / outline_width pairs
TEXT_STYLE_DEFAULT = ui_text_style(UI_FONT_SIZE, 0, bold=False)
TEXT_STYLE_TAB = ui_text_style(UI_FONT_SIZE_TAB, 0)
TEXT_STYLE_TITLE = ui_text_style(UI_FONT_SIZE_TITLE, OUTLINE_STROKE_WIDTH)
TEXT_STYLE_COLLECTION = ui_text_style(
    UI_FONT_SIZE_COLLECTION,
    COLLECTION_OUTLINE_STROKE_WIDTH,
)
TEXT_STYLE_COLLECTION_SMALL = ui_text_style(
    UI_FONT_SIZE_COLLECTION_SMALL,
    COLLECTION_OUTLINE_STROKE_WIDTH,
)

def paint_ui_text(
    painter: QPainter,
    text: str,
    x: float,
    baseline: float,
    style: UiTextStyle,
    *,
    font: QFont | None = None,
) -> None:
    """Draw text with optional outline using *style* (central paint path)."""
    if not text:
        return
    paint_font = font or style.font()
    path = QPainterPath()
    path.addText(x, baseline, paint_font, text)

    if not style.has_outline():
        painter.fillPath(path, QBrush(QColor(style.fill)))
        return

    stroke_color = QColor(style.stroke)
    fill_color = QColor(style.fill)

    if style.outline_mode == "stroker":
        stroker = QPainterPathStroker()
        stroker.setWidth(float(max(3, style.outline_width * 2 + 1)))
        stroker.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        stroker.setCapStyle(Qt.PenCapStyle.RoundCap)
        outline = stroker.createStroke(path)
        painter.fillPath(outline, QBrush(stroke_color))
        painter.fillPath(path, QBrush(fill_color))
        return

    pen = QPen(stroke_color, float(style.outline_width))
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    painter.strokePath(path, pen)
    painter.fillPath(path, QBrush(fill_color))


def text_metrics(style: UiTextStyle, text: str) -> QFontMetrics:
    return QFontMetrics(style.font())


def apply_app_font(app: QApplication | None = None) -> None:
    target = app or QApplication.instance()
    if target is not None:
        target.setFont(TEXT_STYLE_DEFAULT.font())
