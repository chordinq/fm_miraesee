from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Property, QObject, Signal

from core.format.number_format import format_power
from core.game_logic.player.player_model import PlayerModel
from ui.utils.ui_settings import register_display_refresh


def _uint128_to_int(low: int, high: int) -> int:
	return (high << 64) + low


class PlayerStatsBridge(QObject):
	changed = Signal()

	def __init__(
		self,
		player_getter: Callable[[], PlayerModel],
		parent: QObject | None = None,
	) -> None:
		super().__init__(parent)
		self._player_getter = player_getter
		self._power_text = ""
		self._damage = 0.0
		self._health = 0.0
		self._power_low = 0
		self._power_high = 0
		register_display_refresh(self.refresh)

	def refresh(self) -> None:
		player = self._player_getter()
		power_model = player.player_power_model
		power_model.update_power(player, publish_update=True)

		stats = power_model.stats
		config = player.game_config
		if stats is not None:
			power_stats = stats.without_secondary_stats(config)
			self._damage = power_stats.player_damage(config, player.is_ranged)
			self._health = power_stats.player_health(config)
		else:
			self._damage = 0.0
			self._health = 0.0

		power = power_model.power
		self._power_low = power.low
		self._power_high = power.high
		self._power_text = format_power(_uint128_to_int(power.low, power.high))
		self.changed.emit()

	@Property(str, notify=changed)
	def powerText(self) -> str:
		return self._power_text

	@Property(int, notify=changed)
	def powerLow(self) -> int:
		return self._power_low

	@Property(int, notify=changed)
	def powerHigh(self) -> int:
		return self._power_high

	@Property(float, notify=changed)
	def playerDamage(self) -> float:
		return self._damage

	@Property(float, notify=changed)
	def playerHealth(self) -> float:
		return self._health
