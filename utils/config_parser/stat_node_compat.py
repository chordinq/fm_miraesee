"""Map new StatNode wire JSON to legacy StatTargetBase JSON."""

from __future__ import annotations

from typing import Any

from .dump_schema import SchemaRegistry

_QUALIFIER_ENUM_FIELDS: dict[str, dict[str, str]] = {
    "ItemType": {"ItemType": "ItemType"},
    "AttackType": {"AttackType": "AttackType"},
    "Rarity": {
        "Rarity": "Rarity",
        "MountRarity": "Rarity",
        "PetRarity": "Rarity",
        "EggRarity": "Rarity",
    },
    "Skill": {"SkillType": "CombatSkill"},
    "CurrencyType": {"CurrencyType": "CurrencyType"},
    "DungeonType": {"DungeonType": "DungeonType"},
    "Source": {"Source": "Source"},
}


def _enum_name(registry: SchemaRegistry, enum_type: str, value: Any) -> Any:
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return registry.enum_name(enum_type, value)
    return value


def _qualifier_map(
    qualifiers: list[dict[str, Any]] | None,
    registry: SchemaRegistry,
) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for qual in qualifiers or []:
        qtype = qual.get("Type")
        raw_value = qual.get("Value")
        if qtype is None or raw_value is None:
            continue
        field_map = _QUALIFIER_ENUM_FIELDS.get(qtype, {})
        for json_field, enum_type in field_map.items():
            if json_field not in out:
                out[json_field] = _enum_name(registry, enum_type, raw_value)
                break
    return out


def legacy_stat_target_from_node(
    stat_node: dict[str, Any],
    registry: SchemaRegistry,
) -> dict[str, Any]:
    legacy = stat_node.get("LegacyTarget")
    if isinstance(legacy, dict) and legacy.get("$type"):
        return legacy

    existing = stat_node.get("StatTarget")
    if isinstance(existing, dict) and existing.get("$type"):
        return existing

    target = stat_node.get("Target")
    if not isinstance(target, dict):
        return {"$type": "PlayerStatTarget"}

    kind = target.get("Kind", "Player")
    layer = stat_node.get("Layer", "None")
    condition = stat_node.get("Condition", "None")
    quals = _qualifier_map(target.get("Qualifiers"), registry)

    if kind == "Player":
        if layer == "Skins":
            return {"$type": "PlayerSkinMultiplierStatTarget"}
        if condition == "Melee":
            return {"$type": "PlayerMeleeOnlyStatTarget"}
        if condition == "Ranged":
            return {"$type": "PlayerRangedOnlyStatTarget"}
        return {"$type": "PlayerStatTarget"}

    if kind == "Equipment":
        if "AttackType" in quals:
            return {"$type": "WeaponStatTarget", **quals}
        return {"$type": "EquipmentStatTarget", **quals}

    if kind == "ActiveSkill":
        return {"$type": "ActiveSkillStatTarget", **quals}

    if kind == "PassiveSkill":
        return {"$type": "PassiveSkillStatTarget", **quals}

    if kind == "Mount":
        return {"$type": "MountStatTarget", **quals}

    if kind == "Pet":
        return {"$type": "PetStatTarget", **quals}

    if kind == "Egg":
        return {"$type": "EggStatTarget", **quals}

    if kind == "Forge":
        return {"$type": "ForgeStatTarget"}

    if kind == "TechTree":
        return {"$type": "TechTreeStatTarget"}

    if kind == "Duration":
        return {"$type": "OfflineTimerStatTarget"}

    if kind == "Currency":
        if quals:
            return {"$type": "OfflineCurrencyStatTarget", **quals}
        return {"$type": "CurrencyBonusStatTarget", **quals}

    if "DungeonType" in quals or "CurrencyType" in quals:
        return {"$type": "DungeonStatTarget", **quals}

    return {"$type": "PlayerStatTarget"}


def _is_stat_node(value: dict[str, Any]) -> bool:
    return "UniqueStat" in value and (
        "Target" in value or "LegacyTarget" in value or "Layer" in value or "Condition" in value
    )


def normalize_stat_nodes(value: Any, registry: SchemaRegistry) -> Any:
    if isinstance(value, dict):
        if _is_stat_node(value):
            out = {key: normalize_stat_nodes(item, registry) for key, item in value.items()}
            out["StatTarget"] = legacy_stat_target_from_node(out, registry)
            return out
        return {key: normalize_stat_nodes(item, registry) for key, item in value.items()}
    if isinstance(value, list):
        return [normalize_stat_nodes(item, registry) for item in value]
    return value
