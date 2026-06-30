from __future__ import annotations

"""Metaplay F64 fixed-point helpers (32 fractional bits). IL: Metaplay.Core.Math.F64."""

F64_SCALE = 1 << 32


def f64_to_raw(value: float) -> int:
	"""IL: F64 implicit conversion from double truncates toward zero."""
	return int(value * F64_SCALE)


def f64_from_raw(raw: int) -> float:
	if raw >= 0x8000000000000000:
		raw -= 1 << 64
	return raw / F64_SCALE


def f64_clamp01_raw(raw: int) -> int:
	"""IL: F64.Clamp01(F64) on raw fixed-point storage."""
	if raw < 0:
		return 0
	if raw > F64_SCALE:
		return F64_SCALE
	return raw


def f64_clamp01(value: float) -> float:
	"""IL: F64.Clamp01(value)"""
	raw = f64_to_raw(value)
	if raw < 0:
		raw = 0
	elif raw > F64_SCALE:
		raw = F64_SCALE
	return f64_from_raw(raw)


def f64_lerp(lower: float, upper: float, t: float) -> float:
	"""IL: F64.Lerp(lower, upper, Clamp01(t))"""
	return f64_from_raw(f64_lerp_raw(lower, upper, t))


def f64_lerp_raw(lower: float, upper: float, t: float) -> int:
	"""IL: F64.Lerp raw result before get_Double."""
	a = f64_to_raw(lower)
	b = f64_to_raw(upper)
	tr = f64_to_raw(f64_clamp01(t))
	return a + ((b - a) * tr >> 32)


def f64_lerp_raw_from_t_raw(lower: float, upper: float, t_raw: int) -> int:
	"""IL: F64.Lerp with interpolation already stored as F64.Raw."""
	a = f64_to_raw(lower)
	b = f64_to_raw(upper)
	tr = f64_clamp01_raw(t_raw)
	return a + ((b - a) * tr >> 32)
