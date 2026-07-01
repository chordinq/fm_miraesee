from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Union

from core.metaplaymath.int128 import i64
from core.metaplaymath.types import F64Raw

"""Metaplay F64 fixed-point (32 fractional bits). IL: Metaplay.Core.Math.F64."""

F64_SCALE = 1 << 32
F64_ONE_RAW = F64_SCALE
F64_MIN_RAW = -(1 << 63)
_TO_DOUBLE = 1.0 / F64_SCALE

F64Like = Union["F64", int, float]


def f64_to_raw(value: float) -> F64Raw:
	"""IL: F64.FromDouble — truncate toward zero; overflow → MinValue."""
	if math.isinf(value):
		return F64Raw(F64_MIN_RAW)
	return F64Raw(int(value * F64_SCALE))


def f64_from_raw(raw: int) -> float:
	"""IL: F64.get_Double."""
	return i64(raw) * _TO_DOUBLE


def f64_clamp01_raw(raw: int) -> F64Raw:
	"""IL: F64.Clamp01 on raw storage."""
	raw = i64(raw)
	if raw < 0:
		return F64Raw(0)
	if raw > F64_ONE_RAW:
		return F64Raw(F64_ONE_RAW)
	return F64Raw(raw)


def f64_clamp01(value: float) -> float:
	return f64_from_raw(f64_clamp01_raw(f64_to_raw(value)))


def f64_mul_raw(a: int, b: int) -> F64Raw:
	"""IL: F64.op_Multiply."""
	a &= 0xFFFFFFFFFFFFFFFF
	b &= 0xFFFFFFFFFFFFFFFF
	result = (
		(i64(a) >> 32) * b
		+ (i64(b) >> 32) * (a & 0xFFFFFFFF)
		+ ((a & 0xFFFFFFFF) * (b & 0xFFFFFFFF) >> 32)
	)
	return F64Raw(i64(result))


def f64_add_raw(a: int, b: int) -> F64Raw:
	"""IL: F64.op_Addition."""
	return F64Raw(i64(a) + i64(b))


def f64_sub_raw(a: int, b: int) -> F64Raw:
	"""IL: F64.op_Subtraction."""
	return F64Raw(i64(a) - i64(b))


def f64_less_than_raw(a: int, b: int) -> bool:
	"""IL: F64.op_LessThan."""
	return i64(a) < i64(b)


def f64_lerp_raw(a: int, b: int, t: int) -> F64Raw:
	"""IL: F64.Lerp(a, b, Clamp01(t)) with full 64-bit fixed-point multiply."""
	a &= 0xFFFFFFFFFFFFFFFF
	b &= 0xFFFFFFFFFFFFFFFF
	t = f64_clamp01_raw(t)
	one_minus_t = (1 << 32) - t
	result = (
		(i64(b) >> 32) * t
		+ (i64(t) >> 32) * (b & 0xFFFFFFFF)
		+ one_minus_t * (i64(a) >> 32)
		+ ((t & 0xFFFFFFFF) * (b & 0xFFFFFFFF) >> 32)
		+ (i64(one_minus_t) >> 32) * (a & 0xFFFFFFFF)
		+ ((one_minus_t & 0xFFFFFFFF) * (a & 0xFFFFFFFF) >> 32)
	)
	return F64Raw(i64(result))


def f64_lerp_raw_from_t_raw(lower: float, upper: float, t_raw: int) -> F64Raw:
	"""IL: F64.Lerp(FromDouble(lower), FromDouble(upper), t)."""
	return f64_lerp_raw(f64_to_raw(lower), f64_to_raw(upper), t_raw)


def f64_lerp_raw_from_floats(lower: float, upper: float, t: float) -> F64Raw:
	return f64_lerp_raw(f64_to_raw(lower), f64_to_raw(upper), f64_to_raw(f64_clamp01(t)))


def f64_lerp(lower: float, upper: float, t: float) -> float:
	return f64_from_raw(f64_lerp_raw_from_floats(lower, upper, t))


def f64_next_f64_in_range_raw(min_raw: int, max_raw: int, roll_raw: int) -> F64Raw:
	"""IL: RandomPCG.NextF64InRange — min + roll * (max - min)."""
	span = f64_sub_raw(max_raw, min_raw)
	product = f64_mul_raw(roll_raw, span)
	return f64_add_raw(min_raw, product)


def _coerce_raw(value: F64Like) -> int:
	if isinstance(value, F64):
		return value.raw
	if isinstance(value, float):
		return f64_to_raw(value)
	return int(value)


@dataclass(frozen=True, slots=True)
class F64:
	raw: int

	@classmethod
	def from_double(cls, value: float) -> F64:
		return cls(f64_to_raw(value))

	@classmethod
	def from_raw(cls, raw: int) -> F64:
		return cls(i64(raw))

	def to_double(self) -> float:
		return f64_from_raw(self.raw)

	def clamp01(self) -> F64:
		return F64(f64_clamp01_raw(self.raw))

	def lerp(self, other: F64, t: F64) -> F64:
		return F64(f64_lerp_raw(self.raw, other.raw, t.raw))
