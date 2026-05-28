# ui/theme/config/equipment_slots.py — forge equipment grid order
from __future__ import annotations

from core.enums import ItemType

FORGE_EQUIP_TOP: tuple[ItemType, ...] = (
    ItemType.Helmet,
    ItemType.Armour,
    ItemType.Gloves,
    ItemType.Necklace,
    ItemType.Ring,
)

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
