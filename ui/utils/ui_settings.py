from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import QObject, Property, Signal, Slot
from PySide6.QtGui import QGuiApplication

_display_refresh_handlers: list[Callable[[], None]] = []
_economy_refresh_handlers: list[Callable[[], None]] = []
_instance: UiSettingsBridge | None = None


def precise_number_enabled() -> bool:
	if _instance is None:
		return False
	return _instance._precise_number_enabled


def game_number_formatting_enabled() -> bool:
	return not precise_number_enabled()


def allow_negative_currency_enabled() -> bool:
	if _instance is None:
		return False
	return _instance._allow_negative_currency


def register_display_refresh(handler: Callable[[], None]) -> None:
	_display_refresh_handlers.append(handler)


def register_economy_refresh(handler: Callable[[], None]) -> None:
	_economy_refresh_handlers.append(handler)


class UiSettingsBridge(QObject):
	preciseNumberChanged = Signal()
	allowNegativeCurrencyChanged = Signal()
	fullScreenEnabledChanged = Signal()

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._precise_number_enabled = False
		self._allow_negative_currency = False
		self._full_screen_enabled = False

	@Property(bool, notify=preciseNumberChanged)
	def preciseNumberEnabled(self) -> bool:
		return self._precise_number_enabled

	@Property(bool, notify=allowNegativeCurrencyChanged)
	def allowNegativeCurrencyEnabled(self) -> bool:
		return self._allow_negative_currency

	@Property(bool, notify=fullScreenEnabledChanged)
	def fullScreenEnabled(self) -> bool:
		return self._full_screen_enabled

	@Slot(bool)
	def setPreciseNumberEnabled(self, enabled: bool) -> None:
		if self._precise_number_enabled == enabled:
			return
		self._precise_number_enabled = enabled
		self.preciseNumberChanged.emit()
		self._notify_display_refresh_handlers()

	@Slot(bool)
	def setAllowNegativeCurrencyEnabled(self, enabled: bool) -> None:
		if self._allow_negative_currency == enabled:
			return
		self._allow_negative_currency = enabled
		self.allowNegativeCurrencyChanged.emit()
		self._notify_economy_refresh_handlers()

	@Slot(bool)
	def setFullScreenEnabled(self, enabled: bool) -> None:
		if self._full_screen_enabled == enabled:
			return
		self._full_screen_enabled = enabled
		self.fullScreenEnabledChanged.emit()
		self._apply_full_screen(enabled)

	def _apply_full_screen(self, enabled: bool) -> None:
		for window in QGuiApplication.topLevelWindows():
			if enabled:
				window.showFullScreen()
			else:
				window.showNormal()

	def _notify_display_refresh_handlers(self) -> None:
		live_handlers: list[Callable[[], None]] = []
		for handler in _display_refresh_handlers:
			try:
				handler()
				live_handlers.append(handler)
			except RuntimeError:
				continue
		_display_refresh_handlers[:] = live_handlers

	def _notify_economy_refresh_handlers(self) -> None:
		for handler in _economy_refresh_handlers:
			handler()


def register_ui_settings(engine) -> UiSettingsBridge:
	global _instance
	from core.game_logic.player.player_currency_model import register_negative_currency_policy

	_instance = UiSettingsBridge(parent=engine)
	register_negative_currency_policy(allow_negative_currency_enabled)
	engine.rootContext().setContextProperty("UiSettings", _instance)
	return _instance
