from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Union

from core.metaplaymath import int128
from core.metaplaymath.f64 import F64_MIN_RAW, f64_to_raw
from core.metaplaymath.types import FD6Raw

"""Metaplay FD6 fixed-point (6 decimal digits). IL: Metaplay.Core.Math.FD6."""

FD6_PRECISION = 1_000_000

FD6Like = Union["FD6", int, float]


def fd6_from_f64_raw(f64_raw: int) -> FD6Raw:
	"""IL: FD6.FromF64 — (Int128(F64.Raw) * Precision) >> 32."""
	scaled = (int128.i64(f64_raw) * FD6_PRECISION) >> 32
	return FD6Raw(int128.from_i64(scaled))


def fd6_from_f64(value: float) -> float:
	"""Convert double → FD6 semantic float (display / legacy float paths)."""
	return fd6_to_double(fd6_from_f64_raw(f64_to_raw(value)))


def fd6_from_int(value: int) -> FD6Raw:
	"""IL: FD6.FromInt."""
	return FD6Raw(int128.mul(int128.from_i64(value), FD6_PRECISION))


def fd6_from_long(value: int) -> FD6Raw:
	"""IL: FD6.FromLong."""
	return FD6Raw(int128.mul(int128.from_i64(value), FD6_PRECISION))


def fd6_from_double(value: float) -> FD6Raw:
	"""IL: FD6.FromDouble — int part * Precision + fractional part * Precision."""
	if math.isinf(value):
		int_part = F64_MIN_RAW
	else:
		int_part = int(value)
	int_scaled = int128.mul(int_part, FD6_PRECISION)
	frac_scaled = int((value - float(int_part)) * FD6_PRECISION)
	return FD6Raw(int128.add(int_scaled, frac_scaled))


def fd6_to_double(raw: int) -> float:
	"""IL: FD6.get_Double."""
	return int128.to_double(raw) / FD6_PRECISION


def fd6_add_raw(a: int, b: int) -> FD6Raw:
	"""IL: FD6.op_Addition."""
	return FD6Raw(int128.add(a, b))


def fd6_sub_raw(a: int, b: int) -> FD6Raw:
	"""IL: FD6.op_Subtraction."""
	return FD6Raw(int128.sub(a, b))


def fd6_mul_raw(a: int, b: int) -> FD6Raw:
	"""IL: FD6.op_Multiply(FD6, FD6) — product / Precision."""
	product = int128.mul(a, b)
	return FD6Raw(int128.div(product, FD6_PRECISION))


def fd6_mul_f64_raw(f64_raw: int, fd6_raw: int) -> FD6Raw:
	"""IL: FD6.Mul(F64, FD6) — decomposed 64-bit F64 multiply on FD6 scale."""
	f64_raw &= 0xFFFFFFFFFFFFFFFF
	f64_hi = int128.i64(f64_raw) >> 32
	f64_lo = f64_raw & 0xFFFFFFFF
	fd6_hi = int128.rshift(fd6_raw, 32)
	fd6_lo = int128.low_u32(fd6_raw)
	part_a = int128.mul(f64_hi, fd6_raw)
	part_b = int128.rshift(int128.mul(f64_lo, fd6_lo), 32)
	part_c = int128.mul(f64_lo, fd6_hi)
	return FD6Raw(int128.add(int128.add(part_a, part_b), part_c))


def fd6_div_raw(a: int, b: int) -> FD6Raw:
	"""IL: FD6.op_Division — (a * Precision) / b."""
	numerator = int128.mul(a, FD6_PRECISION)
	return FD6Raw(int128.div(numerator, b))


def fd6_less_than_raw(a: int, b: int) -> bool:
	"""IL: FD6.op_LessThan."""
	return int128.less_than(a, b)


def fd6_get_double(value: float) -> float:
	"""IL: FD6.get_Double when value is already in FD6 semantic space."""
	return value


def fd6_truncate(value: float) -> float:
	"""Truncate toward zero at FD6.Precision granularity (UI helper)."""
	return math.trunc(value * FD6_PRECISION) / FD6_PRECISION


def format_fd6_raw(value: float) -> str:
	"""UI raw display: exact FD6 semantic value, no K/M suffix."""
	truncated = fd6_truncate(value)
	if truncated == int(truncated) and abs(truncated) < 1e15:
		return str(int(truncated))
	text = f"{truncated:.6f}".rstrip("0").rstrip(".")
	return text


def _coerce_raw(value: FD6Like) -> int:
	if isinstance(value, FD6):
		return value.raw
	if isinstance(value, float):
		return fd6_from_double(value)
	if isinstance(value, int):
		return fd6_from_int(value)
	return int(value)


@dataclass(frozen=True, slots=True)
class FD6:
	raw: int

	@classmethod
	def from_f64_raw(cls, f64_raw: int) -> FD6:
		return cls(fd6_from_f64_raw(f64_raw))

	@classmethod
	def from_double(cls, value: float) -> FD6:
		return cls(fd6_from_double(value))

	@classmethod
	def from_int(cls, value: int) -> FD6:
		return cls(fd6_from_int(value))

	def to_double(self) -> float:
		return fd6_to_double(self.raw)

	def __add__(self, other: FD6Like) -> FD6:
		return FD6(fd6_add_raw(self.raw, _coerce_raw(other)))

	def __sub__(self, other: FD6Like) -> FD6:
		return FD6(fd6_sub_raw(self.raw, _coerce_raw(other)))

	def __mul__(self, other: FD6Like) -> FD6:
		return FD6(fd6_mul_raw(self.raw, _coerce_raw(other)))

	def __truediv__(self, other: FD6Like) -> FD6:
		return FD6(fd6_div_raw(self.raw, _coerce_raw(other)))

	def __lt__(self, other: FD6Like) -> bool:
		return fd6_less_than_raw(self.raw, _coerce_raw(other))
