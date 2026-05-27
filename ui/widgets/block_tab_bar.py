# ui/widgets/block_tab_bar.py — flush square tabs (no Chrome gaps)
from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QHBoxLayout, QPushButton, QWidget

from ui.constants.colors import DOMAIN_COLORS
from ui.constants.domains import DOMAIN_TAB_LOC_IDS, DOMAINS
from ui.constants.layout import GEAR_TAB_WIDTH, TAB_BAR_HEIGHT
from ui.constants.styles import tab_button_style
from ui.services.localization import translate_id


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

        self._buttons: dict[str, QPushButton] = {}
        for key in DOMAINS:
            loc_id = DOMAIN_TAB_LOC_IDS[key]
            btn = QPushButton(translate_id(loc_id))
            btn.setCheckable(True)
            btn.setProperty("domain", key)
            btn.setProperty("loc_id", loc_id)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(self._on_tab_click)
            btn.setFixedHeight(TAB_BAR_HEIGHT)
            btn.setStyleSheet(
                tab_button_style(active=False, domain_color=DOMAIN_COLORS.get(key))
            )
            row.addWidget(btn, 1)
            self._buttons[key] = btn

        gear = QPushButton("⚙")
        gear.setFixedSize(GEAR_TAB_WIDTH, TAB_BAR_HEIGHT)
        gear.setCursor(Qt.CursorShape.PointingHandCursor)
        gear.clicked.connect(self.options_pressed.emit)
        gear.setStyleSheet(tab_button_style(active=False, gear=True))
        row.addWidget(gear)

        self.set_active("profile")

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

    def refresh_locale(self) -> None:
        active = next((k for k, b in self._buttons.items() if b.isChecked()), "profile")
        for key, btn in self._buttons.items():
            loc_id = DOMAIN_TAB_LOC_IDS.get(key)
            if loc_id is not None:
                btn.setText(translate_id(loc_id))
        self.set_active(active)
