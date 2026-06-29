from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import Property, QObject, Signal, Slot

from ui.utils.timer_display import format_timer_duration
from ui.utils.ui_settings import register_display_refresh

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
        register_display_refresh(self._on_display_refresh)

    def _on_display_refresh(self) -> None:
        self.displayChanged.emit()

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
        return timer.start_time > 0

    @Property(bool, notify=displayChanged)
    def isComplete(self) -> bool:
        timer = self._timer
        player = self._player
        if timer is None or player is None:
            return False
        if timer.start_time <= 0:
            return False
        return timer.has_ended(player)

    @Property(float, notify=displayChanged)
    def progressFraction(self) -> float:
        timer = self._timer
        player = self._player
        if timer is None or player is None or timer.start_time <= 0:
            return 0.0
        if self.isComplete:
            return 1.0
        return float(timer.get_progress(player))

    @Property(str, notify=displayChanged)
    def remainingText(self) -> str:
        if not self.isActive or self.isComplete:
            return ""
        assert self._timer is not None and self._player is not None
        remaining = self._timer.calculate_remaining_seconds(self._player)
        return format_timer_duration(remaining, self._ui_language)

    @Property(int, notify=displayChanged)
    def remainingSeconds(self) -> int:
        if not self.isActive or self.isComplete:
            return 0
        assert self._timer is not None and self._player is not None
        return self._timer.calculate_remaining_seconds(self._player)

    @Slot()
    def refresh(self) -> None:
        self.displayChanged.emit()
