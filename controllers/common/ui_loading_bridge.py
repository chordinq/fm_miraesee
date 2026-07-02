from __future__ import annotations

from PySide6.QtCore import QEventLoop, QObject, Property, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QJSValue
from PySide6.QtQuick import QQuickWindow

_instance: UiLoadingBridge | None = None


def _wait_for_next_frame(max_wait_ms: int = 50) -> None:
	app = QGuiApplication.instance()
	if app is None:
		return
	for window in app.topLevelWindows():
		if not isinstance(window, QQuickWindow):
			continue
		loop = QEventLoop()
		done = False

		def finish() -> None:
			nonlocal done
			if done:
				return
			done = True
			loop.quit()

		window.frameSwapped.connect(finish)
		QTimer.singleShot(max_wait_ms, finish)
		window.update()
		QGuiApplication.processEvents()
		loop.exec()
		try:
			window.frameSwapped.disconnect(finish)
		except (RuntimeError, TypeError):
			pass
		return
	QGuiApplication.processEvents()


class UiLoadingBridge(QObject):
	activeChanged = Signal()

	def __init__(self, parent: QObject | None = None) -> None:
		super().__init__(parent)
		self._depth = 0

	@Property(bool, notify=activeChanged)
	def active(self) -> bool:
		return self._depth > 0

	@Slot()
	def begin(self) -> None:
		self._depth += 1
		self.activeChanged.emit()

	@Slot()
	def end(self) -> None:
		if self._depth <= 0:
			return
		self._depth -= 1
		self.activeChanged.emit()

	@Slot("QJSValue")
	def defer(self, callback: QJSValue) -> None:
		if not callback.isCallable():
			return
		self.begin()
		QGuiApplication.processEvents()
		QTimer.singleShot(0, lambda: self._start_after_paint(callback))

	def _start_after_paint(self, callback: QJSValue) -> None:
		QGuiApplication.processEvents()
		_wait_for_next_frame()
		self._run_js(callback)

	def _run_js(self, callback: QJSValue) -> None:
		try:
			callback.call()
		finally:
			QTimer.singleShot(0, self.end)


def register_ui_loading(engine) -> UiLoadingBridge:
	global _instance
	_instance = UiLoadingBridge(parent=engine)
	engine.rootContext().setContextProperty("UiLoading", _instance)
	return _instance


def ui_loading() -> UiLoadingBridge | None:
	return _instance
