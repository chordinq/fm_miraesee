from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Signal, Slot

from timer_display import format_timer_duration

if TYPE_CHECKING:
    from core.game_logic.player.player_model import PlayerModel
    from core.game_logic.player.timer_model import TimerModel


class TimerBarBridge(QObject):
    """QML-facing TimerModel state for ProgressBar (IL: UpgradeTimerView + ReactiveUpgradeTimer)."""

    displayChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._timer: TimerModel | None = None
        self._player: PlayerModel | None = None
        self._ui_language = "en"

    def bind(
        self,
        timer: TimerModel,
        player: PlayerModel,
        *,
        language: str = "en",
    ) -> None:
        self._timer = timer
        self._player = player
        self._ui_language = language
        self.displayChanged.emit()

    def clear(self) -> None:
        self._timer = None
        self._player = None
        self.displayChanged.emit()

    def set_ui_language(self, language: str) -> None:
        if language == self._ui_language:
            return
        self._ui_language = language
        self.displayChanged.emit()

    @Property(bool, notify=displayChanged)
    def isActive(self) -> bool:
        timer = self._timer
        player = self._player
        if timer is None or player is None:
            return False
        return timer.end_time > timer.start_time

    @Property(bool, notify=displayChanged)
    def isComplete(self) -> bool:
        if not self.isActive:
            return False
        assert self._timer is not None and self._player is not None
        return self._timer.has_ended(self._player)

    @Property(float, notify=displayChanged)
    def progressFraction(self) -> float:
        if not self.isActive:
            return 0.0
        assert self._timer is not None and self._player is not None
        if self._timer.has_ended(self._player):
            return 1.0
        return float(self._timer.get_progress(self._player))

    @Property(str, notify=displayChanged)
    def remainingText(self) -> str:
        if not self.isActive or self.isComplete:
            return ""
        assert self._timer is not None and self._player is not None
        remaining = self._timer.calculate_remaining_seconds(self._player)
        return format_timer_duration(remaining, self._ui_language)

    @Property(int, notify=displayChanged)
    def remainingSeconds(self) -> int:
        if not self.isActive:
            return 0
        assert self._timer is not None and self._player is not None
        return self._timer.calculate_remaining_seconds(self._player)

    @Slot()
    def refresh(self) -> None:
        self.displayChanged.emit()
