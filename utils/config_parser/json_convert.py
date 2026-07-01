"""Convert raw tagged field values to JSON using dump.cs schemas."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .derived_types import resolve_type_name
from .dump_schema import ClassSchema, SchemaRegistry, get_registry
from .game_types import decode_item_id
from .stat_node_compat import normalize_stat_nodes

DEFAULT_DUMP = Path(__file__).resolve().parents[2] / "data" / "dump.cs"

PRIMITIVE_TYPES = frozenset(
    {
        "int",
        "long",
        "uint",
        "bool",
        "string",
        "float",
        "double",
        "F32",
        "F64",
        "F32Vec2",
        "F64Vec2",
        "F32Vec3",
        "F64Vec3",
    }
)


def _resolve_abstract(raw: dict[int, Any], base: str, registry: SchemaRegistry) -> dict[str, Any]:
    raw = dict(raw)
    disc = raw.pop("$type", None)
    type_name = base
    if isinstance(disc, int):
        type_name = resolve_type_name(base, disc, registry.dump_path)
    cls = registry.get_class(type_name)
    if cls and cls.members:
        named = fields_to_json(raw, cls, registry)
        named["$type"] = type_name
        return named
    if isinstance(disc, int):
        return {"$type": type_name, **{str(k): v for k, v in raw.items()}}
    return {str(k): v for k, v in raw.items()}


def dict_key_repr(obj: dict[str, Any]) -> str:
    return str(obj).replace('"', "'")


def convert_value(raw: Any, type_name: str, registry: SchemaRegistry) -> Any:
    base = type_name.rstrip("?")
    if raw is None:
        return None

    if base in registry.enums:
        if isinstance(raw, int):
            return registry.enum_name(base, raw)
        return raw

    if base == "ItemId":
        if isinstance(raw, dict):
            return decode_item_id(raw)
        return raw

    if base.startswith("List<") and base.endswith(">"):
        inner = base[5:-1]
        if isinstance(raw, list):
            inner_cls = registry.get_class(inner)
            if inner_cls:
                return [
                    fields_to_json(item, inner_cls, registry) if isinstance(item, dict) else item
                    for item in raw
                ]
            return [convert_value(v, inner, registry) for v in raw]
        return raw

    if base.endswith("[]"):
        inner = base[:-2]
        if isinstance(raw, list):
            return [convert_value(v, inner, registry) for v in raw]
        return raw

    if base in ("F32", "F64"):
        return float(raw)

    if base in ("F32Vec2", "F64Vec2"):
        return raw

    if base == "bool":
        return bool(raw)

    if base in PRIMITIVE_TYPES:
        return raw

    cls = registry.get_class(base)
    if cls and isinstance(raw, dict) and "$type" in raw:
        return _resolve_abstract(raw, base, registry)
    if cls and isinstance(raw, dict):
        return fields_to_json(raw, cls, registry)

    if isinstance(raw, list):
        return [convert_value(v, base, registry) for v in raw]

    if isinstance(raw, dict):
        return {str(k): convert_value(v, base, registry) for k, v in raw.items()}

    return raw


def fields_to_json(fields: dict[int, Any], schema: ClassSchema, registry: SchemaRegistry) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for tag, member in sorted(schema.members.items()):
        if tag not in fields:
            continue
        raw = fields[tag]
        value = convert_value(raw, member.type_name, registry)
        if member.type_name.rstrip("?") == "bool" and isinstance(raw, int):
            value = bool(raw)
        elif isinstance(value, int) and member.type_name.rstrip("?") in registry.enums:
            value = registry.enum_name(member.type_name.rstrip("?"), value)
        out[member.name] = value
    return out


ENUM_KEY_FIELDS: dict[str, list[str]] = {
    "CombatSkill": ["Type"],
    "SecondaryStatType": ["Stat"],
    "Rarity": ["Rarity", "PetRarity"],
    "DungeonType": ["DungeonType"],
    "TechTreeType": ["Type"],
    "TechTreeNodeType": ["Type", "NodeType"],
    "PetBalancingType": ["Type"],
    "ItemType": ["SkinType", "Type"],
    "UniqueStat": ["Stat"],
    "AscendableType": ["Type"],
    "GuildTier": ["Tier"],
    "ShopResourceId": ["Id"],
    "ForgeLevelKey": ["LevelKey"],
    "ProgressKeyBase": ["Key", "ProgressKey"],
    "PetId": ["PetId"],
    "MountId": ["MountId"],
    "SkinId": ["SkinId"],
    "BattleId": ["BattleId"],
    "InAppProductId": ["ProductId", "Id"],
    "PlayerSegmentId": ["SegmentId", "Id"],
    "DailyDealType": ["DailyDealType", "Type"],
}


def library_key(row: dict[str, Any], key_type: str, registry: SchemaRegistry) -> str:
    if key_type == "ForgeLevelKey" and isinstance(row.get("LevelKey"), dict):
        return dict_key_repr(row["LevelKey"])

    if key_type == "ProgressKeyBase" and "ProgressKey" in row:
        return dict_key_repr(row["ProgressKey"])

    if key_type == "PlayerSegmentId" and isinstance(row.get("SegmentId"), str):
        return row["SegmentId"]

    if key_type == "InAppProductId":
        if isinstance(row.get("ProductId"), str):
            return row["ProductId"]
        if "Rewards" in row:
            return str(row["Rewards"])

    if key_type == "int":
        for name in ("ConfigKey", "Level", "EnemyIdx", "Id", "Idx"):
            if name in row:
                return str(row[name])
        for v in row.values():
            if isinstance(v, int) and not isinstance(v, bool):
                return str(v)
        raise ValueError(f"cannot infer int library key from {row}")

    if key_type in registry.enums:
        for fname in ENUM_KEY_FIELDS.get(key_type, ["Type", "Stat", "Rarity", "Id"]):
            if fname not in row:
                continue
            val = row[fname]
            if isinstance(val, str):
                return val
            if isinstance(val, int):
                return str(registry.enum_name(key_type, val))
        raise ValueError(f"cannot infer enum library key {key_type} from {row}")

    if key_type == "ItemId":
        item = row.get("ItemId") or row.get("ConfigKey")
        if item is None:
            raise ValueError(f"missing ItemId key in {row}")
        return dict_key_repr(item)

    cls = registry.get_class(key_type)
    if cls and cls.members:
        key_obj: dict[str, Any] = {}
        for member in cls.members.values():
            if member.name in row:
                key_obj[member.name] = row[member.name]
        if key_obj:
            return dict_key_repr(key_obj)

    for nested_name in (key_type, "BattleId", "ConfigKey", "Id"):
        nested = row.get(nested_name)
        if isinstance(nested, dict):
            return dict_key_repr(nested)
        if isinstance(nested, str):
            return nested

    raise ValueError(f"unsupported library key type {key_type}: {row}")


def decode_mpc(blob: bytes, entry_name: str, registry: SchemaRegistry | None = None) -> Any:
    registry = registry or get_registry()
    entry = registry.entries.get(entry_name)
    if not entry:
        raise KeyError(f"unknown config entry {entry_name}")

    if entry.kind == "keyvalue":
        from .meta_reader import parse_tagged_root

        fields = parse_tagged_root(blob)
        cls = registry.get_class(entry.class_name)
        if not cls:
            raise ValueError(f"missing class schema {entry.class_name}")
        return normalize_stat_nodes(fields_to_json(fields, cls, registry), registry)

    from .meta_reader import parse_object_table

    rows, _ = parse_object_table(blob)
    cls = registry.get_class(entry.class_name)
    if not cls:
        raise ValueError(f"missing class schema {entry.class_name}")

    out: dict[str, Any] = {}
    for fields in rows:
        row_json = fields_to_json(fields, cls, registry)
        key = library_key(row_json, entry.key_type or "int", registry)
        out[key] = row_json
    return normalize_stat_nodes(out, registry)
