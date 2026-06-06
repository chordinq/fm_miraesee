from __future__ import annotations

import time
import uuid
from typing import Iterable, Sequence, TypeVar

T = TypeVar("T")


class RandomPCG:
	_MASK64: int = 0xFFFFFFFFFFFFFFFF
	_MUL: int = 0x5851F42D4C957F2D
	_INC_CREATE: int = 0x1A08EE1184BA6D32
	_INC_NEXT: int = 0x14057B7EF767814F
	_U32_DENOM: int = 4_294_967_296
	_U16_DENOM: int = 65_536
	_TO_DOUBLE01: float = 2.3283064365386963e-10 

	@staticmethod
	def _mask64(value: int) -> int:
		return value & RandomPCG._MASK64

	@staticmethod
	def _mask32(value: int) -> int:
		return value & 0xFFFFFFFF

	def __init__(self, seed: int | RandomPCG | None = None) -> None:
		if isinstance(seed, RandomPCG):
			self._state = seed._state
		elif seed is None:
			self._state = 0
		else:
			self._state = self._mask64(int(seed) * self._MUL + self._INC_CREATE)

	@classmethod
	def create_from_seed(cls, seed: int) -> RandomPCG:
		return cls(seed)

	@classmethod
	def create_new(cls) -> RandomPCG:
		return cls(cls._random_seed())

	@classmethod
	def _random_seed(cls) -> int:
		tick_a = int(time.time() * 1000) & 0xFFFFFFFF
		guid_a = uuid.uuid4().int & 0xFFFFFFFF
		tick_b = int(time.time() * 1000) & 0xFFFFFFFF
		guid_b = uuid.uuid4().int & 0xFFFFFFFF
		low = guid_b ^ tick_b
		high = guid_a ^ tick_a
		return cls._mask64(low | (high << 32))

	def _advance(self) -> None:
		self._state = self._mask64(self._state * self._MUL + self._INC_NEXT)

	def _next_pcg32(self) -> int:
		old = self._state
		hi = self._mask32(old >> 32)
		lo = self._mask32(old >> 27)
		xorshifted = self._mask32((hi >> 13) ^ lo)
		rot = hi >> 27
		self._state = self._mask64(old * self._MUL + self._INC_NEXT)
		return self._mask32((xorshifted << ((-rot) & 0x1F)) + (xorshifted >> rot))

	def next_uint(self) -> int:
		return self._next_pcg32()

	def next_int(self, max_exclusive: int | None = None) -> int:
		raw = self._next_pcg32() >> 1
		if max_exclusive is None:
			return raw
		if max_exclusive <= 0:
			raise ValueError("maxExclusive must be positive")
		return raw - (raw // max_exclusive) * max_exclusive

	def next_int_min_max(self, min_inclusive: int, max_exclusive: int) -> int:
		if max_exclusive - min_inclusive == 0 or min_inclusive > max_exclusive:
			raise ValueError("invalid int range")
		return min_inclusive + self.next_int(max_exclusive - min_inclusive)

	def next_ulong(self) -> int:
		high = self._next_pcg32()
		low = self._next_pcg32()
		return self._mask64((high << 32) | low)

	def next_long(self, max_exclusive: int | None = None) -> int:
		value = self.next_ulong() >> 1
		if max_exclusive is None:
			return value
		if max_exclusive <= 0:
			raise ValueError("maxExclusive must be positive")
		return value - (value // max_exclusive) * max_exclusive

	def next_float(self) -> float:
		return float(self._next_pcg32()) / float(self._U32_DENOM)

	def next_double(self) -> float:
		return float(self._next_pcg32()) / float(self._U32_DENOM)

	def next_f32_bits(self) -> int:
		return self._next_pcg32() & 0xFFFF

	def next_f32(self) -> float:
		return float(self.next_f32_bits()) / float(self._U16_DENOM)

	def next_f64_bits(self) -> int:
		return self._next_pcg32()

	def next_f64(self) -> float:
		return float(self.next_f64_bits()) / float(self._U32_DENOM)

	def next_f64_in_range(self, min_value: float, max_value: float) -> float:
		return min_value + self.next_f64() * (max_value - min_value)

	def next_fixed_d6(self) -> float:
		"""Returns a float in [0, 1) equivalent to IL's FD6.FromF64(NextF64()).

		IL: NextF64 produces a raw uint32 PCG value; FD6.FromF64 converts it
		via floor(raw * 1_000_000 / 2^32) = floor(float_value * 1_000_000).
		The returned Python float matches the F64 float value exactly.
		Callers that need the integer FD6 representation should compute
		int(next_fixed_d6() * 1_000_000) themselves (as roll_stat does).
		"""
		return self.next_f64()

	def next_bool(self) -> bool:
		return (self._next_pcg32() >> 31) != 0

	def choice(self, items: Sequence[T] | Iterable[T]) -> T:
		if isinstance(items, Sequence):
			count = len(items)
			if count < 1:
				raise ValueError("choice() called with empty sequence")
			return items[self.next_int(count)]

		selected: T | None = None
		bound = 1
		for item in items:
			roll = self.next_int(bound)
			if selected is None or roll == 0:
				selected = item
			bound += 1
		if selected is None:
			raise ValueError("choice() called with empty sequence")
		return selected

	def next_guid(self) -> str:
		part1 = self.next_ulong()
		part2 = self.next_ulong()
		return f"{part1:016X}-{part2:016X}"

	def __eq__(self, other: object) -> bool:
		if self is other:
			return True
		if not isinstance(other, RandomPCG):
			return False
		return self._state == other._state

	def __hash__(self) -> int:
		return hash(self._state)

	def __repr__(self) -> str:
		return f"RandomPCG(state=0x{self._state:016X})"
