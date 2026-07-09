from __future__ import annotations

import ast
from dataclasses import dataclass

from config import WEAPON_LIBRARY
from core.game_logic.attacks_system import (
	AttackCycleMetrics as CoreAttackCycleMetrics,
	attack_cycle_metrics as core_attack_cycle_metrics,
	simulate_double_cycle_seconds,
	simulate_primary_cycle_seconds,
)
from core.game_logic.player.game_tick import player_model_game_tick_seconds
from core.game_logic.unit_constants import DOUBLE_ATTACK_SPEED_UP


@dataclass(frozen=True, slots=True)
class WeaponTiming:
	age: int
	idx: int
	windup_time: float
	attack_duration: float
	attack_range: float
	is_ranged: bool

	@property
	def recovery_time(self) -> float:
		return self.attack_duration - self.windup_time


@dataclass(slots=True)
class AttackCycleMetrics:
	attack_speed_bonus_pct: float
	attack_speed_multi: float
	windup_seconds: float
	recovery_seconds: float
	primary_cycle_seconds: float
	game_tick_cycle_seconds: float
	game_tick_bpm: float
	double_hit_delay_seconds: float
	double_cycle_seconds: float
	primary_attacks_per_second: float
	game_tick_attacks_per_second: float
	double_attacks_per_second: float


def attack_speed_multi_from_bonus_pct(bonus_pct: float) -> float:
	return 1.0 + bonus_pct / 100.0


def _parse_weapon_key(key: str) -> tuple[int, int]:
	parsed = ast.literal_eval(key)
	return int(parsed["Age"]), int(parsed["Idx"])


def weapon_timing_from_library(*, weapon_idx: int, age: int) -> WeaponTiming:
	for key, row in WEAPON_LIBRARY.items():
		entry_age, entry_idx = _parse_weapon_key(key)
		if entry_idx == weapon_idx and entry_age == age:
			return WeaponTiming(
				age=entry_age,
				idx=entry_idx,
				windup_time=float(row["WindupTime"]),
				attack_duration=float(row["AttackDuration"]),
				attack_range=float(row["AttackRange"]),
				is_ranged=bool(row["IsRanged"]),
			)
	raise KeyError(f"weapon Idx={weapon_idx} Age={age} not found in WeaponLibrary.json")


def _to_legacy_metrics(core: CoreAttackCycleMetrics) -> AttackCycleMetrics:
	return AttackCycleMetrics(
		attack_speed_bonus_pct=(core.attack_speed_multi - 1.0) * 100.0,
		attack_speed_multi=core.attack_speed_multi,
		windup_seconds=core.windup_seconds,
		recovery_seconds=core.recovery_seconds,
		primary_cycle_seconds=core.continuous_cycle_seconds,
		game_tick_cycle_seconds=core.game_tick_cycle_seconds,
		game_tick_bpm=core.game_tick_bpm,
		double_hit_delay_seconds=core.double_hit_delay_seconds,
		double_cycle_seconds=core.double_cycle_seconds,
		primary_attacks_per_second=core.continuous_attacks_per_second,
		game_tick_attacks_per_second=core.game_tick_attacks_per_second,
		double_attacks_per_second=1.0 / core.double_cycle_seconds
		if core.double_cycle_seconds > 0.0
		else 0.0,
	)


def analytic_cycle_metrics(
	weapon: WeaponTiming,
	*,
	attack_speed_multi: float,
) -> AttackCycleMetrics:
	core = core_attack_cycle_metrics(
		windup_duration=weapon.windup_time,
		attack_duration=weapon.attack_duration,
		attack_speed_multi=attack_speed_multi,
	)
	return _to_legacy_metrics(core)


def game_tick_seconds() -> float:
	return player_model_game_tick_seconds()


@dataclass(frozen=True, slots=True)
class AttackSpeedBreakpointRow:
	min_bonus_pct: float
	attack_speed_multi: float
	cycle_seconds: float
	double_cycle_seconds: float
	aps: float
	double_aps: float


def attack_speed_breakpoint_rows(
	weapon: WeaponTiming,
	*,
	pct_max: float = 400.0,
) -> tuple[AttackSpeedBreakpointRow, ...]:
	rows: list[AttackSpeedBreakpointRow] = []
	prev_cycle: float | None = None
	prev_double_cycle: float | None = None
	limit = int(pct_max * 100)
	for pct_x100 in range(0, limit + 1):
		pct = pct_x100 / 100.0
		speed = attack_speed_multi_from_bonus_pct(pct)
		cycle = simulate_primary_cycle_seconds(
			windup_duration=weapon.windup_time,
			attack_duration=weapon.attack_duration,
			attack_speed_multi=speed,
		)
		double_cycle = simulate_double_cycle_seconds(
			windup_duration=weapon.windup_time,
			attack_duration=weapon.attack_duration,
			attack_speed_multi=speed,
		)
		cycle_changed = prev_cycle is None or cycle < prev_cycle - 1e-9
		double_changed = (
			prev_double_cycle is None or double_cycle < prev_double_cycle - 1e-9
		)
		if cycle_changed or double_changed:
			rows.append(
				AttackSpeedBreakpointRow(
					min_bonus_pct=pct,
					attack_speed_multi=speed,
					cycle_seconds=cycle,
					double_cycle_seconds=double_cycle,
					aps=1.0 / cycle if cycle > 0.0 else 0.0,
					double_aps=1.0 / double_cycle if double_cycle > 0.0 else 0.0,
				)
			)
			prev_cycle = cycle
			prev_double_cycle = double_cycle
	return tuple(rows)
