"""Shared enum / struct helpers for game config decoding."""

from __future__ import annotations

from typing import Any

ITEM_TYPE_NAMES: dict[int, str] = {
    0: "Helmet",
    1: "Armour",
    2: "Gloves",
    3: "Necklace",
    4: "Ring",
    5: "Weapon",
    6: "Shoes",
    7: "Belt",
}


def decode_item_id(value: dict[int, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "Age": value[1],
        "Type": ITEM_TYPE_NAMES.get(value[2], str(value[2])),
        "Idx": value[3],
    }
