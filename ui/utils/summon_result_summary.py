from __future__ import annotations

from ui.utils.localizer import rarity_loc_from_rarity

_EMPTY_RESULT: dict[str, object] = {
    "hasData": False,
    "paidCount": 0,
    "totalPulls": 0,
    "bonusRolls": 0,
    "rarityRows": [],
}


def build_summon_result_summary(
    preview: list[dict[str, object]],
    paid_count: int,
) -> dict[str, object]:
    if not preview:
        return dict(_EMPTY_RESULT)

    total_pulls = len(preview)
    bonus_rolls = max(0, total_pulls - paid_count)

    rarity_counts: dict[int, int] = {}
    for entry in preview:
        rarity = int(entry.get("rarity", -1))
        if rarity < 0:
            continue
        rarity_counts[rarity] = rarity_counts.get(rarity, 0) + 1

    rarity_rows: list[dict[str, object]] = []
    for rarity in sorted(rarity_counts.keys(), reverse=True):
        loc_id, loc_table = rarity_loc_from_rarity(rarity)
        rarity_rows.append(
            {
                "rarity": rarity,
                "count": rarity_counts[rarity],
                "rarityLocId": loc_id,
                "rarityLocTable": loc_table,
            }
        )

    return {
        "hasData": True,
        "paidCount": paid_count,
        "totalPulls": total_pulls,
        "bonusRolls": bonus_rolls,
        "rarityRows": rarity_rows,
    }
