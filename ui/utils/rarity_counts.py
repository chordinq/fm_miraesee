from __future__ import annotations

RARITY_COUNT = 6


def build_rarity_counts(counts: list[int]) -> list[dict[str, int]]:
    return [{"rarity": rarity, "count": counts[rarity]} for rarity in range(RARITY_COUNT)]


def count_rarities(items, rarity_getter) -> list[dict[str, int]]:
    counts = [0] * RARITY_COUNT
    for item in items:
        rarity = int(rarity_getter(item))
        if 0 <= rarity < RARITY_COUNT:
            counts[rarity] += 1
    return build_rarity_counts(counts)
