# ui/services/locale.py — UI language selection (en / ko / ja)
from __future__ import annotations

from enum import Enum
from typing import Literal

from PySide6.QtCore import QObject, QSettings, Signal

LanguageCode = Literal["en", "ko", "ja"]


class Language(str, Enum):
    EN = "en"
    KO = "ko"
    JA = "ja"

    @classmethod
    def from_code(cls, code: str) -> Language:
        try:
            return cls(code)
        except ValueError:
            return cls.EN


class LocaleService(QObject):
    """Global UI language; persists via QSettings."""

    changed = Signal()

    _SETTINGS_KEY = "ui/language"

    def __init__(self) -> None:
        super().__init__()
        stored = QSettings("Miraesee", "Miraesee").value(self._SETTINGS_KEY, Language.EN.value)
        self._language = Language.from_code(str(stored))

    @property
    def language(self) -> Language:
        return self._language

    def set_language(self, language: Language) -> None:
        if language == self._language:
            return
        self._language = language
        QSettings("Miraesee", "Miraesee").setValue(self._SETTINGS_KEY, language.value)
        self.changed.emit()

    def code(self) -> LanguageCode:
        return self._language.value  # type: ignore[return-value]


locale_service = LocaleService()
