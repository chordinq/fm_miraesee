# ui/views/options_dialog.py — language settings modal
from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from ui.constants.styles import muted_button_style, primary_button_style
from ui.services.locale import Language, locale_service
from ui.services.localization import LANGUAGE_NATIVE_LABELS, ui_text


class OptionsDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(ui_text("settings"))
        self.setModal(True)
        self.setMinimumWidth(280)

        root = QVBoxLayout(self)
        root.setContentsMargins(16, 16, 16, 16)
        root.setSpacing(12)

        lang_row = QHBoxLayout()
        lang_lbl = QLabel(ui_text("language"))
        lang_lbl.setStyleSheet("background: transparent;")
        self._lang_combo = QComboBox()
        self._lang_combo.addItem(LANGUAGE_NATIVE_LABELS["en"], Language.EN.value)
        self._lang_combo.addItem(LANGUAGE_NATIVE_LABELS["ko"], Language.KO.value)
        self._lang_combo.addItem(LANGUAGE_NATIVE_LABELS["ja"], Language.JA.value)
        idx = self._lang_combo.findData(locale_service.language.value)
        if idx >= 0:
            self._lang_combo.setCurrentIndex(idx)
        lang_row.addWidget(lang_lbl)
        lang_row.addWidget(self._lang_combo, 1)
        root.addLayout(lang_row)

        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        close_btn = QPushButton(ui_text("close"))
        close_btn.setStyleSheet(muted_button_style())
        close_btn.clicked.connect(self.accept)
        apply_btn = QPushButton(ui_text("ok"))
        apply_btn.setStyleSheet(primary_button_style())
        apply_btn.clicked.connect(self._apply)
        btn_row.addWidget(close_btn)
        btn_row.addWidget(apply_btn)
        root.addLayout(btn_row)

    def _apply(self) -> None:
        code = self._lang_combo.currentData()
        if code is not None:
            locale_service.set_language(Language.from_code(str(code)))
        self.accept()
