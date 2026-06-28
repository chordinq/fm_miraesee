from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Property, Signal, Slot

_refresh_handlers: list[Callable[[], None]] = []
_instance: UiSettingsBridge | None = None


def game_number_formatting_enabled() -> bool:
	if _instance is None:
		return True
	return _instance._game_number_formatting


def allow_negative_currency_enabled() -> bool:
	if _instance is None:
		return False
	return _instance._allow_negative_currency


def register_display_refresh(handler: Callable[[], None]) -> None:
	_refresh_handlers.append(handler)


class UiSettingsBridge(QObject):
	gameNumberFormattingChanged = Signal()
	allowNegativeCurrencyChanged = Signal()

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._game_number_formatting = True
		self._allow_negative_currency = False

	@Property(bool, notify=gameNumberFormattingChanged)
	def gameNumberFormattingEnabled(self) -> bool:
		return self._game_number_formatting

	@Property(bool, notify=allowNegativeCurrencyChanged)
	def allowNegativeCurrencyEnabled(self) -> bool:
		return self._allow_negative_currency

	@Slot(bool)
	def setGameNumberFormattingEnabled(self, enabled: bool) -> None:
		if self._game_number_formatting == enabled:
			return
		self._game_number_formatting = enabled
		self.gameNumberFormattingChanged.emit()
		self._notify_refresh_handlers()

	@Slot(bool)
	def setAllowNegativeCurrencyEnabled(self, enabled: bool) -> None:
		if self._allow_negative_currency == enabled:
			return
		self._allow_negative_currency = enabled
		self.allowNegativeCurrencyChanged.emit()
		self._notify_refresh_handlers()

	def _notify_refresh_handlers(self) -> None:
		for handler in _refresh_handlers:
			handler()


def register_ui_settings(engine) -> UiSettingsBridge:
	global _instance
	_instance = UiSettingsBridge(parent=engine)
	engine.rootContext().setContextProperty("UiSettings", _instance)
	return _instance
