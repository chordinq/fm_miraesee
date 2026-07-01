from __future__ import annotations

"""Signed Int128 helpers. IL: Dirichlet.Numerics.Int128 (FD6.Raw storage)."""

_MASK128 = (1 << 128) - 1


def i64(value: int) -> int:
	value &= 0xFFFFFFFFFFFFFFFF
	if value >= 0x8000000000000000:
		value -= 1 << 64
	return value


def sign_extend_128(value: int) -> int:
	value &= _MASK128
	if value >= (1 << 127):
		value -= 1 << 128
	return value


def from_i64(value: int) -> int:
	return sign_extend_128(i64(value))


def add(a: int, b: int) -> int:
	return sign_extend_128((sign_extend_128(a) + sign_extend_128(b)) & _MASK128)


def sub(a: int, b: int) -> int:
	return sign_extend_128((sign_extend_128(a) - sign_extend_128(b)) & _MASK128)


def mul(a: int, b: int) -> int:
	return sign_extend_128((sign_extend_128(a) * sign_extend_128(b)) & _MASK128)


def div(a: int, b: int) -> int:
	b_signed = sign_extend_128(b)
	if b_signed == 0:
		raise ZeroDivisionError("Int128 division by zero")
	a_signed = sign_extend_128(a)
	return sign_extend_128(a_signed // b_signed)


def less_than(a: int, b: int) -> bool:
	return sign_extend_128(a) < sign_extend_128(b)


def rshift(value: int, bits: int) -> int:
	return sign_extend_128(sign_extend_128(value) >> bits)


def low_u32(value: int) -> int:
	return sign_extend_128(value) & 0xFFFFFFFF


def to_double(value: int) -> float:
	return float(sign_extend_128(value))
