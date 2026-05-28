# ui/views/shell/hub_div.py — tab bar + domain pages
from __future__ import annotations

from PySide6.QtWidgets import QApplication, QStackedWidget, QSizePolicy, QVBoxLayout, QWidget

from ui.theme.config.domains import DOMAINS
from ui.views.collection.mount_collection_view import MountCollectionView
from ui.views.collection.pet_collection_view import PetCollectionView
from ui.views.collection.skill_collection_view import SkillCollectionView
from ui.services.locale import locale_service
from features.session import Session
from ui.theme.fonts import apply_app_font
from ui.theme.stylesheet import global_stylesheet
from ui.views.coming_soon_view import ComingSoonView
from ui.views.forge_view import ForgeView
from ui.views.options_dialog import OptionsDialog
from ui.widgets.block_tab_bar import BlockTabBar


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
            "profile": ComingSoonView,
            "forge": ForgeView,
            "skill": SkillCollectionView,
            "pet": PetCollectionView,
            "mount": MountCollectionView,
            "techtree": ComingSoonView,
        }
        for key in DOMAINS:
            factory = _domain_views[key]
            page = factory(session)
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
        app = QApplication.instance()
        if app is not None:
            apply_app_font(app)
            app.setStyleSheet(global_stylesheet())
        if hasattr(self._tabs, "refresh_locale"):
            self._tabs.refresh_locale()
        for page in self._sections.values():
            if hasattr(page, "refresh_locale"):
                page.refresh_locale()
