"""IL: LocalizationSettings.SelectedLocale — global UI locale for QML + bridges."""
from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.format.localizer_base import (
	load_available_languages,
	selected_language,
	set_selected_language,
)

_instance: UiLocaleBridge | None = None
_locale_refresh_handlers: list = []


def register_locale_refresh(handler) -> None:
	_locale_refresh_handlers.append(handler)


class UiLocaleBridge(QObject):
	selectedLocaleChanged = Signal()

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._languages = load_available_languages()
		self._selected_code = selected_language()

	@Property("QVariantList", constant=True)
	def languages(self) -> list[dict[str, str]]:
		return self._languages

	@Property(str, notify=selectedLocaleChanged)
	def selectedCode(self) -> str:
		return self._selected_code

	@Property(bool, notify=selectedLocaleChanged)
	def isEnglish(self) -> bool:
		return self._selected_code == "en"

	@Slot(str)
	def setSelectedLocale(self, code: str) -> None:
		if not code or code == self._selected_code:
			return
		self._selected_code = code
		set_selected_language(code)
		self.selectedLocaleChanged.emit()
		for handler in _locale_refresh_handlers:
			handler(code)


def sync_ui_locale(code: str) -> None:
	if _instance is None or not code:
		return
	_instance.setSelectedLocale(code)


def register_ui_locale(engine) -> UiLocaleBridge:
	global _instance
	_instance = UiLocaleBridge(parent=engine)
	engine.rootContext().setContextProperty("UiLocale", _instance)
	return _instance
