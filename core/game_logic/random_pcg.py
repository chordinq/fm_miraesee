from __future__ import annotations
from typing import Sequence, TypeVar

_MASK64     = 0xFFFFFFFFFFFFFFFF
_MUL        = 0x5851F42D4C957F2D
_INC_CREATE = 0x1A08EE1184BA6D32
_INC_NEXT   = 0x14057B7EF767814F

U32_DENOM = 4_294_967_296

T = TypeVar("T")

def _mask64(v: int) -> int: return v & _MASK64
def _mask32(v: int) -> int: return v & 0xFFFFFFFF

class RandomPCG:
	def __init__(self, seed: int) -> None:
		self._state: int = _mask64(seed * _MUL + _INC_CREATE)

	def _next_pcg32(self) -> int:
		old = self._state
		self._state = _mask64(old * _MUL + _INC_NEXT)
		xorshifted = _mask32(((old >> 18) ^ old) >> 27)
		rot = (old >> 59) & 0x1F
		return _mask32((xorshifted << ((~rot + 1) & 0x1F)) + (xorshifted >> rot))

	def next_f64(self) -> float:
		return self._next_pcg32() / U32_DENOM

	def next_int(self, max_val: int) -> int:
		if max_val <= 0:
			return 0
		raw = self._next_pcg32()
		pos = (raw >> 1) & 0x7FFFFFFF
		return pos - (pos // max_val) * max_val

	def next_int_min_max(self, min_inclusive: int, max_exclusive: int) -> int:
		if max_exclusive <= min_inclusive:
			return min_inclusive
		return min_inclusive + self.next_int(max_exclusive - min_inclusive)

	def choice(self, items: Sequence[T]) -> T:
		if not items:
			raise ValueError("choice() called with empty sequence")
		selected = items[0]
		for bound, item in enumerate(items, 1):
			if self.next_int(bound) == 0:
				selected = item
		return selected

	def next_ulong(self) -> int:
		high = self._next_pcg32()
		low  = self._next_pcg32()
		return _mask64((high << 32) | low)

	def next_guid(self) -> str:
		part1 = self.next_ulong()
		part2 = self.next_ulong()
		return f"{part1:016X}-{part2:016X}"
