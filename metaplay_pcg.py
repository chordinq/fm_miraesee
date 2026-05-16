# metaplay_pcg.py

class MetaplayPCG:
    def __init__(self, seed: int):
        self.state = (seed * 0x5851f42d4c957f2d + 0x1a08ee1184ba6d32) & 0xFFFFFFFFFFFFFFFF

    def _next_pcg32(self) -> int:
        old_state = self.state
        self.state = (old_state * 0x5851f42d4c957f2d + 0x14057b7ef767814f) & 0xFFFFFFFFFFFFFFFF
        xorshifted = (((old_state >> 18) ^ old_state) >> 27) & 0xFFFFFFFF
        rot = (old_state >> 59) & 0x1F
        left_shift = (xorshifted << ((~rot + 1) & 0x1F)) & 0xFFFFFFFF
        right_shift = (xorshifted >> rot) & 0xFFFFFFFF
        return (left_shift + right_shift) & 0xFFFFFFFF

    def next_f64(self) -> float:
        return self._next_pcg32() / 4294967296.0

    def next_int(self, max_val: int) -> int:
        if max_val <= 0: return 0
        raw = self._next_pcg32()
        pos_val = (raw >> 1) & 0x7FFFFFFF 
        div = pos_val // max_val
        return pos_val - (div * max_val)

    def choice(self, items: list):
        selected = None
        count = 1
        for item in items:
            roll = self.next_int(count)
            if roll == 0:
                selected = item
            count += 1
        return selected

    def next_ulong(self) -> int:
        high = self._next_pcg32()
        low = self._next_pcg32()
        return ((high << 32) | low) & 0xFFFFFFFFFFFFFFFF

    def next_guid(self):
        part1 = self.next_ulong()
        part2 = self.next_ulong()
        return f"{part1:016X}-{part2:016X}"