# ui/constants/styles.py — QSS builders (global + per-widget)
from __future__ import annotations

from ui.constants.colors import (
    ACCENT,
    ACCENT_HOVER,
    BG,
    BG_PANEL,
    BTN_MUTED,
    COLLECTION_BG,
    HATCH_BAR_BG,
    FG,
    FG_MUTED,
    TAB_ACTIVE,
    TAB_BORDER,
    TILE_PLACEHOLDER,
)
from ui.constants.layout import TAB_BAR_HEIGHT


def global_stylesheet() -> str:
    return f"""
* {{
    margin: 0;
    padding: 0;
    border: none;
    outline: none;
    color: {FG};
    background-color: {BG};
    font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
    font-size: 13px;
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

QWidget#HatchSlotBar {{
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


def _domain_color_inactive(hex_color: str) -> str:
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r}, {g}, {b}, 0.45)"


def tab_button_style(
    *,
    active: bool,
    gear: bool = False,
    domain_color: str | None = None,
) -> str:
    if gear:
        border = f"none; border-left: 1px solid {TAB_BORDER}; border-bottom: 1px solid {TAB_BORDER}"
        bg, color = BG_PANEL, FG_MUTED
    elif domain_color:
        if active:
            border = f"none; border-bottom: 2px solid {domain_color}"
            bg, color = BG_PANEL, domain_color
        else:
            border = f"none; border-right: 1px solid {TAB_BORDER}; border-bottom: 1px solid {TAB_BORDER}"
            bg, color = BG, _domain_color_inactive(domain_color)
    elif active:
        border = f"none; border-bottom: 2px solid {TAB_ACTIVE}"
        bg, color = BG_PANEL, TAB_ACTIVE
    else:
        border = f"none; border-right: 1px solid {TAB_BORDER}; border-bottom: 1px solid {TAB_BORDER}"
        bg, color = BG, FG_MUTED
    hover_color = domain_color if domain_color else FG
    pad_v = max(4, (TAB_BAR_HEIGHT - 14) // 2)
    return f"""
    QPushButton {{
        background-color: {bg};
        color: {color};
        border: {border};
        border-radius: 0px;
        padding: {pad_v}px 0px;
        margin: 0px;
    }}
    QPushButton:hover {{
        background-color: {BG_PANEL};
        color: {hover_color};
    }}
    """


def primary_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {ACCENT};
        color: #ffffff;
        border: 1px solid {ACCENT};
        border-radius: 0px;
        padding: 6px 20px;
        min-width: 88px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    """


def muted_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {BTN_MUTED};
        color: {FG};
        border: 1px solid {TAB_BORDER};
        border-radius: 0px;
        padding: 6px 16px;
        min-width: 72px;
    }}
    QPushButton:hover {{ background-color: {BG_PANEL}; }}
    """


def dump_start_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {ACCENT};
        color: white;
        border: none;
        border-radius: 0px;
        padding: 8px;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    """


def dump_quit_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {BTN_MUTED};
        color: {FG};
        border: 1px solid {TAB_BORDER};
        border-radius: 0px;
        padding: 8px;
    }}
    """


def title_label_style() -> str:
    return f"color: {FG}; font-size: 18px; font-weight: bold; background: transparent;"


def muted_label_style(*, padding: str = "0") -> str:
    return f"color: {FG_MUTED}; background: transparent; padding: {padding};"


def collection_tile_style(*, border_color: str, filled: bool) -> str:
    bg = BG_PANEL if filled else TILE_PLACEHOLDER
    return f"""
    QWidget#CollectionTile {{
        background-color: {bg};
        border: 2px solid {border_color};
    }}
    QLabel#CollectionIcon {{
        background: transparent;
    }}
    QLabel#CollectionName {{
        color: {FG};
        background: transparent;
        font-size: 9px;
        font-weight: bold;
    }}
    QLabel#CollectionMeta {{
        color: {FG_MUTED};
        background: transparent;
        font-size: 8px;
    }}
    """


def tile_placeholder_style() -> str:
    return (
        f"background-color: {TILE_PLACEHOLDER}; "
        f"border: 1px solid {TAB_BORDER}; color: {FG_MUTED};"
    )


def equipment_slot_style(*, filled: bool) -> str:
    name_color = FG if filled else FG_MUTED
    return f"""
    QWidget#EquipSlot {{
        background: transparent;
    }}
    QLabel#EquipSlotType {{
        color: {FG_MUTED};
        background: transparent;
        font-size: 10px;
    }}
    QLabel#EquipSlotIcon {{
        background: transparent;
    }}
    QLabel#EquipSlotName {{
        color: {name_color};
        background: transparent;
        font-size: 10px;
        font-weight: bold;
    }}
    QLabel#EquipSlotMeta {{
        color: {FG_MUTED};
        background: transparent;
        font-size: 10px;
    }}
    """
