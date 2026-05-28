# ui/widgets/block_tab_bar.py — flush square tabs (no Chrome gaps)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.theme.colors import DOMAIN_COLORS
from ui.theme.config.domains import DOMAIN_SUMMON_KIND, DOMAIN_TAB_LOC_IDS, DOMAINS
from ui.theme.fonts import TEXT_STYLE_TAB
from ui.theme.metrics import GEAR_TAB_WIDTH, TAB_BAR_HEIGHT
from ui.theme.builders import tab_button_style
from ui.services.localization import summon_kind_display_name, translate_id


def _tab_label(domain: str) -> str:
    kind = DOMAIN_SUMMON_KIND.get(domain)
    if kind is not None:
        return summon_kind_display_name(kind)
    loc_id = DOMAIN_TAB_LOC_IDS.get(domain)
    return translate_id(loc_id) if loc_id is not None else domain


class BlockTabBar(QWidget):
    """Edge-to-edge tab strip: buttons touch, 0 spacing, square active outline."""

    domain_selected = Signal(str)
    options_pressed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("BlockTabBar")
        self.setFixedHeight(TAB_BAR_HEIGHT)

        row = QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(0)

        self._tab_font = TEXT_STYLE_TAB.font()

        self._buttons: dict[str, QPushButton] = {}
        for key in DOMAINS:
            btn = QPushButton(_tab_label(key))
            self._apply_tab_font(btn)
            btn.setCheckable(True)
            btn.setProperty("domain", key)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._on_tab_click)
            btn.setFixedHeight(TAB_BAR_HEIGHT)
            btn.setStyleSheet(
                tab_button_style(active=False, domain_color=DOMAIN_COLORS.get(key))
            )
            row.addWidget(btn, 1)
            self._buttons[key] = btn

        gear = QPushButton("⚙")
        self._apply_tab_font(gear)
        gear.setFixedSize(GEAR_TAB_WIDTH, TAB_BAR_HEIGHT)
        gear.setCursor(Qt.CursorShape.PointingHandCursor)
        gear.clicked.connect(self.options_pressed.emit)
        gear.setStyleSheet(tab_button_style(active=False, gear=True))
        row.addWidget(gear)

        self.set_active("profile")

    def _apply_tab_font(self, btn: QPushButton) -> None:
        """Re-apply bold after QSS — global * font can override setFont on Windows."""
        btn.setFont(self._tab_font)

    def _on_tab_click(self) -> None:
        btn = self.sender()
        if not isinstance(btn, QPushButton):
            return
        key = btn.property("domain")
        if key:
            self.set_active(str(key))
            self.domain_selected.emit(str(key))

    def set_active(self, domain: str) -> None:
        for key, btn in self._buttons.items():
            btn.setChecked(key == domain)
            btn.setStyleSheet(
                tab_button_style(
                    active=(key == domain),
                    domain_color=DOMAIN_COLORS.get(key),
                )
            )
            self._apply_tab_font(btn)

    def refresh_locale(self) -> None:
        active = next((k for k, b in self._buttons.items() if b.isChecked()), "profile")
        for key, btn in self._buttons.items():
            btn.setText(_tab_label(key))
            self._apply_tab_font(btn)
        self.set_active(active)
