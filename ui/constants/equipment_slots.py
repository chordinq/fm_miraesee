# ui/constants/equipment_slots.py — forge equipment grid order
from __future__ import annotations

from core.enums import ItemType

# Top row (5): helmet → ring
FORGE_EQUIP_TOP: tuple[ItemType, ...] = (
    ItemType.Helmet,
    ItemType.Armour,
    ItemType.Gloves,
    ItemType.Necklace,
    ItemType.Ring,
)

# Bottom row (3): weapon → belt (centered under the top row)
FORGE_EQUIP_BOTTOM: tuple[ItemType, ...] = (
    ItemType.Weapon,
    ItemType.Shoes,
    ItemType.Belt,
)

SLOT_LABELS: dict[ItemType, str] = {
    ItemType.Helmet: "Helmet",
    ItemType.Armour: "Armour",
    ItemType.Gloves: "Gloves",
    ItemType.Necklace: "Necklace",
    ItemType.Ring: "Ring",
    ItemType.Weapon: "Weapon",
    ItemType.Shoes: "Shoes",
    ItemType.Belt: "Belt",
}
