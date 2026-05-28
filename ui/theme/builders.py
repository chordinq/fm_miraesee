# ui/theme/builders.py — per-widget QSS builders
from __future__ import annotations

from ui.theme.colors import (
    ACCENT,
    ACCENT_HOVER,
    BG,
    BG_PANEL,
    BTN_MUTED,
    FG,
    FG_MUTED,
    TAB_ACTIVE,
    TAB_BORDER,
    TILE_PLACEHOLDER,
)
from ui.theme.fonts import UI_FONT_SIZE, UI_FONT_SIZE_TAB, ui_font_family_css
from ui.theme.metrics import TAB_BAR_HEIGHT


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
    family = ui_font_family_css()
    pad_v = max(2, (TAB_BAR_HEIGHT - UI_FONT_SIZE_TAB - 8) // 2)
    return f"""
    QPushButton {{
        background-color: {bg};
        color: {color};
        border: {border};
        border-radius: 0px;
        padding: {pad_v}px 8px;
        margin: 0px;
        font-family: {family};
        font-size: {UI_FONT_SIZE_TAB}pt;
        font-weight: 700;
    }}
    QPushButton:hover {{
        background-color: {BG_PANEL};
        color: {hover_color};
        font-weight: 700;
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


def summon_batch_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: {ACCENT};
        color: #ffffff;
        border: 2px solid #1a1a1a;
        border-radius: 14px;
        padding: 4px 14px;
        min-width: 44px;
        font-weight: bold;
    }}
    QPushButton:hover {{ background-color: {ACCENT_HOVER}; }}
    QPushButton:disabled {{
        background-color: {BTN_MUTED};
        color: {FG_MUTED};
        border-color: {TAB_BORDER};
    }}
    """


def summon_main_button_style() -> str:
    return f"""
    QPushButton {{
        background-color: #b8b8b8;
        color: #ffffff;
        border: 3px solid #1a1a1a;
        border-radius: 8px;
        padding: 8px 16px;
        min-width: 120px;
        min-height: 48px;
        font-weight: bold;
        font-size: 14px;
    }}
    QPushButton:hover {{ background-color: #c8c8c8; }}
    QPushButton:disabled {{
        background-color: {BTN_MUTED};
        color: {FG_MUTED};
        border-color: {TAB_BORDER};
    }}
    """


def summon_combo_style() -> str:
    family = ui_font_family_css()
    return f"""
    QComboBox {{
        background-color: #ffffff;
        color: #1a1a1a;
        border: 2px solid #1a1a1a;
        border-radius: 4px;
        padding: 2px 6px;
        min-width: 52px;
        font-family: {family};
    }}
    QComboBox::drop-down {{
        border: none;
        width: 18px;
    }}
    """


def summon_progress_style() -> str:
    return """
    QProgressBar {
        background-color: #1a1a1a;
        border: 2px solid #1a1a1a;
        border-radius: 6px;
        min-height: 14px;
        max-height: 14px;
        text-align: center;
        color: #ffffff;
        font-weight: bold;
    }
    QProgressBar::chunk {
        background-color: #4a7eb8;
        border-radius: 4px;
    }
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
        background: transparent;
    }}
    """


def tile_placeholder_style() -> str:
    return (
        f"background-color: {TILE_PLACEHOLDER}; "
        f"border: 1px solid {TAB_BORDER}; color: {FG_MUTED};"
    )


def equipment_slot_style(*, filled: bool) -> str:
    _ = filled
    return f"""
    QWidget#EquipSlot {{
        background: transparent;
    }}
    QLabel#EquipSlotType {{
        color: {FG_MUTED};
        background: transparent;
        font-size: 10px;
    }}
    """
