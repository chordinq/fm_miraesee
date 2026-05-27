# ui/views/hub_view.py — tab bar + domain stack
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGridLayout,
    QLabel,
    QScrollArea,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from ui.constants.domains import DOMAINS
from ui.constants.layout import GRID_COLS, GRID_GAP, GRID_MARGIN, TILE_SIZE
from ui.constants.styles import tile_placeholder_style
from ui.services.locale import locale_service
from ui.services.session import Session
from ui.views.forge_view import ForgeView
from ui.views.options_dialog import OptionsDialog
from ui.views.mount_view import MountView
from ui.views.pet_view import PetView
from ui.views.skill_view import SkillView
from ui.widgets.block_tab_bar import BlockTabBar


class _SectionPlaceholder(QWidget):
    def __init__(self, domain: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)

        body = QWidget()
        body_layout = QVBoxLayout(body)
        body_layout.setContentsMargins(0, 0, 0, 0)
        body_layout.setSpacing(0)

        grid_host = QWidget()
        grid = QGridLayout(grid_host)
        grid.setContentsMargins(GRID_MARGIN, GRID_MARGIN, GRID_MARGIN, GRID_MARGIN)
        grid.setSpacing(GRID_GAP)
        for i in range(12):
            tile = QLabel("·")
            tile.setFixedSize(TILE_SIZE, TILE_SIZE)
            tile.setAlignment(Qt.AlignmentFlag.AlignCenter)
            tile.setStyleSheet(tile_placeholder_style())
            grid.addWidget(tile, i // GRID_COLS, i % GRID_COLS)
        body_layout.addWidget(grid_host, 1)

        scroll.setWidget(body)
        outer.addWidget(scroll, 1)


class HubView(QWidget):
    def __init__(self, session: Session, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.session = session

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self._tabs = BlockTabBar()
        root.addWidget(self._tabs)

        self._stack = QStackedWidget()
        self._sections: dict[str, QWidget] = {}
        _domain_views = {
            "forge": ForgeView,
            "skill": SkillView,
            "pet": PetView,
            "mount": MountView,
        }
        for key in DOMAINS:
            factory = _domain_views.get(key)
            if factory is not None:
                page = factory(session)
            else:
                page = _SectionPlaceholder(key)
            page.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self._sections[key] = page
            self._stack.addWidget(page)
        root.addWidget(self._stack, 1)

        self._tabs.domain_selected.connect(self._on_domain)
        self._tabs.options_pressed.connect(self._open_options)
        locale_service.changed.connect(self._refresh_locale)
        self._tabs.set_active("skill")
        self._stack.setCurrentWidget(self._sections["skill"])

    def _on_domain(self, domain: str) -> None:
        self._stack.setCurrentWidget(self._sections[domain])

    def _open_options(self) -> None:
        dlg = OptionsDialog(self)
        dlg.exec()

    def _refresh_locale(self) -> None:
        if hasattr(self._tabs, "refresh_locale"):
            self._tabs.refresh_locale()
        for page in self._sections.values():
            if hasattr(page, "refresh_locale"):
                page.refresh_locale()
