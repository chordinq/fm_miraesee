from PySide6.QtCore import QObject, Property, Signal, Slot

from core.game_logic.enums import SecondaryStatType
from controllers.common.ui_format import (
	format_ui_integer,
	format_ui_max_progress_label,
	format_ui_maxed_progress_label,
	format_ui_percentage_fraction,
	format_ui_percentage_rational,
	format_ui_progress_pair,
	format_ui_secondary_stat,
	format_ui_stat,
)
from ui.utils.ui_settings import register_display_refresh


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

    @Slot(float, float, result=str)
    def formatProgressPair(self, current: float, total: float) -> str:
        return format_ui_progress_pair(current, total)

    @Slot(result=str)
    def maxProgressLabel(self) -> str:
        return format_ui_max_progress_label()

    @Slot(float, result=str)
    def formatPercentageFraction(self, fraction: float) -> str:
        return format_ui_percentage_fraction(fraction)

    @Slot(int, int, result=str)
    def formatPercentageRational(self, level_sum: int, max_sum: int) -> str:
        return format_ui_percentage_rational(level_sum, max_sum)

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
