from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.metaplaymath.f64 import f64_to_raw
from core.metaplaymath.fd6 import (
	fd6_add_raw,
	fd6_from_double,
	fd6_mul_f64_raw,
	fd6_sub_raw,
	fd6_to_double,
)

from ..stats import Stats

if TYPE_CHECKING:
	from .player_model import PlayerModel

_POWER_MULTIPLIER = 3


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
		"""IL: ConsumeUpdate — clear HasUpdate."""
		self.has_update = False

	def update_power(self, player: PlayerModel, publish_update: bool = True) -> None:
		"""IL: UpdatePower — CalculateTotalStats, CalculatePower, optional listener publish."""
		from .player_model import calculate_total_stats

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
	"""IL: PlayerPowerExtensions.CalculatePower."""
	if stats is None:
		raise ValueError("stats is required for PlayerPowerExtensions.CalculatePower")
	if game_config is None:
		raise ValueError("game_config is required for PlayerPowerExtensions.CalculatePower")

	balancing = getattr(game_config, "item_balancing_config", None)
	if balancing is None:
		raise ValueError(
			"item_balancing_config is required for PlayerPowerExtensions.CalculatePower"
		)

	power_stats = stats.without_secondary_stats(game_config)
	player_damage_raw = fd6_from_double(
		power_stats.player_damage(game_config, is_ranged)
	)
	player_health_raw = fd6_from_double(
		power_stats.player_health(game_config)
	)
	base_damage_raw = fd6_from_double(balancing.player_base_damage)
	base_health_raw = fd6_from_double(balancing.player_base_health)

	damage_delta = fd6_sub_raw(player_damage_raw, base_damage_raw)
	health_delta = fd6_sub_raw(player_health_raw, base_health_raw)
	mult_raw = f64_to_raw(balancing.player_power_damage_multiplier)
	combined_raw = fd6_add_raw(
		fd6_mul_f64_raw(mult_raw, damage_delta),
		health_delta,
	)
	scaled_raw = fd6_mul_f64_raw(
		f64_to_raw(float(_POWER_MULTIPLIER)),
		combined_raw,
	)
	return UInt128.from_int(_fd6_round_to_int128(scaled_raw))


def get_mission_level_multiplier(game_config: Any, level: int) -> float:
	"""IL: PlayerPowerExtensions.GetMissionLevelMultiplier."""
	raise NotImplementedError(
		"PlayerPowerExtensions.GetMissionLevelMultiplier — "
		"MissionBaseConfig not wired on SharedGameConfig yet"
	)


def calculate_mission_power(
	game_config: Any,
	level: int,
	hp: int,
	damage: int,
	enemy_count: int,
) -> int:
	"""IL: PlayerPowerExtensions.CalculateMissionPower."""
	raise NotImplementedError(
		"PlayerPowerExtensions.CalculateMissionPower — "
		"MissionBaseConfig not wired on SharedGameConfig yet"
	)


def _fd6_round_to_int128(raw: int) -> int:
	"""IL: FD6.RoundToInt128 — nearest integer from fixed-point storage."""
	return round(fd6_to_double(raw))


PlayerPowerModel.calculate_power = staticmethod(calculate_power)
