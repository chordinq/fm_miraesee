from __future__ import annotations

from dataclasses import dataclass

from core.game_logic.enums import CombatState
from core.game_logic.player.game_tick import PLAYER_MODEL_GAME_TICK_RAW
from core.game_logic.unit_constants import _DOUBLE_ATTACK_REMAINING_WINDUP_FRACTION_RAW
from core.metaplaymath.f64 import f64_add_raw, f64_from_raw, f64_sub_raw
from core.metaplaymath.fd6 import (
	fd6_add_raw,
	fd6_from_double,
	fd6_from_int,
	fd6_greater_than_or_equal_raw,
	fd6_mul_f64_raw,
	fd6_to_double,
)


@dataclass(slots=True)
class AttackCycleMetrics:
	attack_speed_multi: float
	windup_seconds: float
	recovery_seconds: float
	continuous_cycle_seconds: float
	game_tick_cycle_seconds: float
	game_tick_bpm: float
	double_hit_delay_seconds: float
	double_cycle_seconds: float
	continuous_attacks_per_second: float
	game_tick_attacks_per_second: float


@dataclass(slots=True)
class _UnitAttackSim:
	windup_duration_raw: int
	attack_duration_raw: int
	attack_speed_multi_raw: int
	game_tick_raw: int
	state: CombatState = CombatState.Idle
	attack_timer_raw: int = 0
	double_attack_pending: bool = False
	target_in_range: bool = True
	elapsed_raw: int = 0
	force_double_on_first_hit: bool = False
	attacks_fired: int = 0

	def _timer_fill_raw(self) -> int:
		return fd6_mul_f64_raw(self.game_tick_raw, self.attack_speed_multi_raw)

	def step(self) -> None:
		"""IL: AttacksSystem.HandleUnits — one in-range unit, one PlayerModel.GameTick."""
		if self.state is CombatState.Idle:
			self.elapsed_raw = f64_add_raw(self.elapsed_raw, self.game_tick_raw)
			if self.target_in_range:
				self.state = CombatState.WindingUp
			return

		self.attack_timer_raw = fd6_add_raw(self.attack_timer_raw, self._timer_fill_raw())
		self.elapsed_raw = f64_add_raw(self.elapsed_raw, self.game_tick_raw)

		if self.state is CombatState.WindingUp:
			if not fd6_greater_than_or_equal_raw(
				self.attack_timer_raw,
				self.windup_duration_raw,
			):
				return
			self._execute_attack()
			return

		if self.state is CombatState.OnCooldown:
			if not fd6_greater_than_or_equal_raw(
				self.attack_timer_raw,
				self.attack_duration_raw,
			):
				return
			self.state = CombatState.Idle
			self.attack_timer_raw = fd6_from_int(0)
			self.double_attack_pending = False

	def _execute_attack(self) -> None:
		self.attacks_fired += 1
		self.state = CombatState.OnCooldown
		if self.force_double_on_first_hit and self.attacks_fired == 1:
			self.attack_timer_raw = fd6_mul_f64_raw(
				_DOUBLE_ATTACK_REMAINING_WINDUP_FRACTION_RAW,
				self.windup_duration_raw,
			)
			self.double_attack_pending = True
			self.state = CombatState.WindingUp
			return
		if self.double_attack_pending:
			self.double_attack_pending = False

	def run_until_cycles(self, cycle_count: int, *, max_steps: int = 100_000) -> float:
		completed = 0
		steps = 0
		start_raw = self.elapsed_raw
		while completed < cycle_count and steps < max_steps:
			before = self.state
			self.step()
			steps += 1
			if before is CombatState.Idle and self.state is CombatState.WindingUp:
				completed += 1
		if completed < cycle_count:
			raise RuntimeError("attack cycle simulation guard exceeded")
		return f64_from_raw(f64_sub_raw(self.elapsed_raw, start_raw)) / cycle_count


def handle_unit_attack_step(
	*,
	state: CombatState,
	attack_timer_raw: int,
	windup_duration_raw: int,
	attack_duration_raw: int,
	attack_speed_multi_raw: int,
	game_tick_raw: int = PLAYER_MODEL_GAME_TICK_RAW,
	target_in_range: bool = True,
	double_attack_pending: bool = False,
	force_double_proc: bool = False,
	attacks_fired: int = 0,
) -> tuple[CombatState, int, bool, int]:
	"""
	IL: one AttacksSystem.HandleUnits tick for a single sustained in-range unit.

	Returns (state, attack_timer_raw, double_attack_pending, attacks_fired).
	"""
	unit = _UnitAttackSim(
		windup_duration_raw=windup_duration_raw,
		attack_duration_raw=attack_duration_raw,
		attack_speed_multi_raw=attack_speed_multi_raw,
		game_tick_raw=game_tick_raw,
		state=state,
		attack_timer_raw=attack_timer_raw,
		double_attack_pending=double_attack_pending,
		target_in_range=target_in_range,
		force_double_on_first_hit=force_double_proc,
		attacks_fired=attacks_fired,
	)
	unit.step()
	return (
		unit.state,
		unit.attack_timer_raw,
		unit.double_attack_pending,
		unit.attacks_fired,
	)


def double_attack_timer_after_proc(*, windup_duration: float) -> float:
	"""IL: AttackTimer ← WindUpDuration × (1 − 1/DoubleAttackSpeedUp) after first hit."""
	windup_raw = fd6_from_double(windup_duration)
	timer_raw = fd6_mul_f64_raw(_DOUBLE_ATTACK_REMAINING_WINDUP_FRACTION_RAW, windup_raw)
	return fd6_to_double(timer_raw)


def simulate_primary_cycle_seconds(
	*,
	windup_duration: float,
	attack_duration: float,
	attack_speed_multi: float,
	cycles: int = 3,
	game_tick_raw: int = PLAYER_MODEL_GAME_TICK_RAW,
) -> float:
	"""Sustained in-range primary attack cadence under PlayerModel.GameTick (0.1s)."""
	unit = _UnitAttackSim(
		windup_duration_raw=fd6_from_double(windup_duration),
		attack_duration_raw=fd6_from_double(attack_duration),
		attack_speed_multi_raw=fd6_from_double(attack_speed_multi),
		game_tick_raw=game_tick_raw,
	)
	if unit.state is CombatState.Idle and unit.target_in_range:
		unit.state = CombatState.WindingUp
	return unit.run_until_cycles(cycles)


def simulate_double_cycle_seconds(
	*,
	windup_duration: float,
	attack_duration: float,
	attack_speed_multi: float,
	cycles: int = 2,
	game_tick_raw: int = PLAYER_MODEL_GAME_TICK_RAW,
) -> float:
	unit = _UnitAttackSim(
		windup_duration_raw=fd6_from_double(windup_duration),
		attack_duration_raw=fd6_from_double(attack_duration),
		attack_speed_multi_raw=fd6_from_double(attack_speed_multi),
		game_tick_raw=game_tick_raw,
		force_double_on_first_hit=True,
	)
	if unit.state is CombatState.Idle and unit.target_in_range:
		unit.state = CombatState.WindingUp
	total = 0.0
	for _ in range(cycles):
		unit.attacks_fired = 0
		start_raw = unit.elapsed_raw
		steps = 0
		while steps < 100_000:
			before = unit.state
			unit.step()
			steps += 1
			if (
				unit.attacks_fired >= 2
				and before is CombatState.Idle
				and unit.state is CombatState.WindingUp
			):
				total += f64_from_raw(f64_sub_raw(unit.elapsed_raw, start_raw))
				break
		else:
			raise RuntimeError("double-attack cycle simulation guard exceeded")
	return total / cycles


def attack_cycle_metrics(
	*,
	windup_duration: float,
	attack_duration: float,
	attack_speed_multi: float,
	game_tick_raw: int = PLAYER_MODEL_GAME_TICK_RAW,
) -> AttackCycleMetrics:
	speed = attack_speed_multi
	recovery = attack_duration - windup_duration
	continuous = attack_duration / speed if speed > 0.0 else 0.0
	game_tick_cycle = simulate_primary_cycle_seconds(
		windup_duration=windup_duration,
		attack_duration=attack_duration,
		attack_speed_multi=speed,
		game_tick_raw=game_tick_raw,
	)
	timer_after_proc = double_attack_timer_after_proc(windup_duration=windup_duration)
	double_delay = (windup_duration - timer_after_proc) / speed
	double_cycle = game_tick_cycle + double_delay
	return AttackCycleMetrics(
		attack_speed_multi=speed,
		windup_seconds=windup_duration / speed,
		recovery_seconds=recovery / speed,
		continuous_cycle_seconds=continuous,
		game_tick_cycle_seconds=game_tick_cycle,
		game_tick_bpm=60.0 / game_tick_cycle if game_tick_cycle > 0.0 else 0.0,
		double_hit_delay_seconds=double_delay,
		double_cycle_seconds=double_cycle,
		continuous_attacks_per_second=1.0 / continuous if continuous > 0.0 else 0.0,
		game_tick_attacks_per_second=1.0 / game_tick_cycle if game_tick_cycle > 0.0 else 0.0,
	)
