from __future__ import annotations

from core.metaplaymath.f64 import F64_ONE_RAW, f64_div_raw, f64_sub_raw, f64_to_raw

"""IL: Game.Logic.UnitConstants (static cctor)."""

DOUBLE_ATTACK_SPEED_UP = 4.0
DOUBLE_ATTACK_SPEED_UP_RAW = f64_to_raw(DOUBLE_ATTACK_SPEED_UP)

# IL: 1 − (F64.One / DoubleAttackSpeedUp) — remaining windup fraction after first hit.
_DOUBLE_ATTACK_REMAINING_WINDUP_FRACTION_RAW = f64_sub_raw(
	F64_ONE_RAW,
	f64_div_raw(F64_ONE_RAW, DOUBLE_ATTACK_SPEED_UP_RAW),
)
