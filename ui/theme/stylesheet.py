# ui/theme/stylesheet.py — global QSS (single source of truth)
from __future__ import annotations

from ui.theme.colors import (
    BG,
    COLLECTION_BG,
    FG_MUTED,
    HATCH_BAR_BG,
)
from ui.theme.fonts import UI_FONT_SIZE, UI_FONT_SIZE_TAB, ui_font_family_css


def global_stylesheet() -> str:
    family = ui_font_family_css()
    return f"""
* {{
    margin: 0;
    padding: 0;
    border: none;
    outline: none;
    font-family: {family};
    font-size: {UI_FONT_SIZE}px;
}}

QWidget#BlockTabBar QPushButton {{
    font-size: {UI_FONT_SIZE_TAB}pt;
    font-weight: 700;
}}

QMainWindow, QWidget#GameRoot, QStackedWidget {{
    background-color: {BG};
}}

QWidget#CollectionPanel,
QWidget#CollectionFiller,
QScrollArea#CollectionScroll {{
    background-color: {COLLECTION_BG};
}}

QScrollArea {{
    background-color: {BG};
}}

QScrollArea > QWidget > QWidget {{
    background-color: {BG};
}}

QScrollArea#CollectionScroll,
QScrollArea#CollectionScroll > QWidget > QWidget {{
    background-color: {COLLECTION_BG};
}}

QWidget#CollectionPanel QScrollArea > QWidget > QWidget {{
    background-color: transparent;
}}

QWidget#HatchBarRegion {{
    background-color: {HATCH_BAR_BG};
}}

QScrollArea {{
    border: none;
}}
QScrollBar:vertical {{
    width: 0px;
    background: {BG};
}}
QScrollBar:horizontal {{
    height: 0px;
    background: {BG};
}}

QLabel#PlaceholderText {{
    color: {FG_MUTED};
    background: transparent;
}}
"""
