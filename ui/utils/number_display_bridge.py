from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.game_logic.enums import SecondaryStatType
from number_display_format import format_ui_integer
from stat_display_format import format_ui_secondary_stat, format_ui_stat
from ui_settings import register_display_refresh


class NumberDisplayBridge(QObject):
    changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._revision = 0
        register_display_refresh(self._on_display_refresh)

    def _on_display_refresh(self) -> None:
        self._revision += 1
        self.changed.emit()

    @Property(int, notify=changed)
    def revision(self) -> int:
        return self._revision

    @Slot(float, result=str)
    def formatInteger(self, value: float) -> str:
        return format_ui_integer(value)

    @Slot(float, bool, result=str)
    def formatStat(self, value: float, as_multiplier: bool) -> str:
        return format_ui_stat(value, as_multiplier=as_multiplier)

    @Slot(int, float, result=str)
    def formatSecondaryStat(self, stat_type: int, value: float) -> str:
        try:
            return format_ui_secondary_stat(SecondaryStatType(stat_type), value)
        except ValueError:
            return format_ui_stat(value)


def register_number_display(engine) -> NumberDisplayBridge:
    bridge = NumberDisplayBridge(parent=engine)
    engine.rootContext().setContextProperty("NumberDisplay", bridge)
    return bridge
