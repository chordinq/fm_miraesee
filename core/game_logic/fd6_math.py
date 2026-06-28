from __future__ import annotations

import math

from .f64_math import f64_to_raw

"""Metaplay FD6 fixed-point helpers (6 decimal digits). IL: Metaplay.Core.Math.FD6."""

FD6_PRECISION = 1_000_000


def fd6_from_f64_raw(f64_raw: int) -> float:
	"""IL: FD6.FromF64 — (Int128(F64.Raw) * Precision) >> 32."""
	if f64_raw >= 0x8000000000000000:
		f64_raw -= 1 << 64
	scaled = (f64_raw * FD6_PRECISION) >> 32
	return scaled / FD6_PRECISION


def fd6_from_f64(value: float) -> float:
	"""IL: FD6.op_Implicit(F64) → FromF64(F64.Raw)."""
	return fd6_from_f64_raw(f64_to_raw(value))


def fd6_get_double(value: float) -> float:
	"""IL: FD6.get_Double() — value is already FD6 semantic space."""
	return value


def fd6_truncate(value: float) -> float:
	"""Truncate toward zero at FD6.Precision (1_000_000) granularity."""
	return math.trunc(value * FD6_PRECISION) / FD6_PRECISION


def format_fd6_raw(value: float) -> str:
	"""UI raw display: exact FD6 semantic value, no K/M suffix or floor pipeline."""
	truncated = fd6_truncate(value)
	if truncated == int(truncated) and abs(truncated) < 1e15:
		return str(int(truncated))
	text = f"{truncated:.6f}".rstrip("0").rstrip(".")
	return text
