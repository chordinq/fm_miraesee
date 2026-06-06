from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from ..stats import Stats

if TYPE_CHECKING:
	from .player_model import PlayerModel


@dataclass
class UInt128:
	low: int = 0
	high: int = 0

	@classmethod
	def from_int(cls, value: int) -> UInt128:
		mask64 = (1 << 64) - 1
		if value < 0:
			value = value % (1 << 128)
		return cls(low=value & mask64, high=(value >> 64) & mask64)


class PlayerPowerModel:
	def __init__(self) -> None:
		self.has_update = False
		self.power = UInt128()
		self.stats: Stats | None = None

	def consume_update(self) -> None:
		self.has_update = False

	def update_power(self, player: PlayerModel, publish_update: bool = True) -> None:
		from .player_item_stats import calculate_total_stats

		self.has_update = True
		self.stats = calculate_total_stats(player)
		self.power = calculate_power(
			player.game_config,
			self.stats,
			player.is_ranged,
		)
		if publish_update:
			pass

def calculate_power(
	game_config: Any,
	stats: Stats | None,
	is_ranged: bool,
) -> UInt128:
	if stats is None:
		raise ValueError("stats is required for PlayerPowerExtensions.CalculatePower")
	if game_config is None:
		raise ValueError("game_config is required for PlayerPowerExtensions.CalculatePower")

	balancing = getattr(game_config, "item_balancing_config", None)
	if balancing is None:
		raise ValueError(
			"item_balancing_config is required for PlayerPowerExtensions.CalculatePower"
		)

	player_damage = stats.player_damage(game_config, is_ranged)
	player_health = stats.player_health(game_config)
	damage_delta = player_damage - balancing.player_base_damage
	health_delta = player_health - balancing.player_base_health
	combined = balancing.player_power_damage_multiplier * damage_delta + health_delta
	return UInt128.from_int(round(combined * 3))


PlayerPowerModel.calculate_power = staticmethod(calculate_power)
