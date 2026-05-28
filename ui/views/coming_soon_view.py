# ui/views/coming_soon_view.py — placeholder for unfinished hub tabs
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget

from ui.theme.fonts import ui_text_style
from ui.services.localization import ui_text
from features.session import Session
from ui.widgets.outlined_label import OutlinedLabel


class ComingSoonView(QWidget):
    def __init__(self, session: Session | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        _ = session

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.addStretch(1)

        self._label = OutlinedLabel(ui_text("coming_soon"), style=ui_text_style(22, 3))
        root.addWidget(self._label)

        root.addStretch(1)

    def refresh_locale(self) -> None:
        self._label.setText(ui_text("coming_soon"))
