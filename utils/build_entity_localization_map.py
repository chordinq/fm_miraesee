# utils/build_entity_localization_map.py — mapping + enums → en/ko/ja from string tables
"""Build configs/localization/entity_names_en_ko_ja.json."""
from __future__ import annotations

import enum
import inspect
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import core.enums as game_enums
from configs.enum_en_lookup import (
    combat_skill_en_keys_from_mapping,
    currency_en_keys,
    item_age_en_keys,
    item_type_en_keys,
    member_en_key,
    rarity_en_keys,
)

_TABLE_PRIORITY = (
    "Stats",
    "Forge",
    "General",
    "Skills",
    "Pets",
    "Items",
    "Guilds",
    "Shop",
    "Missions",
    "Dungeons",
    "TechTree",
)


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _build_en_index(tables: dict) -> dict[str, dict]:
    index: dict[str, dict] = {}
    for table in _TABLE_PRIORITY:
        for row in tables.get(table, []):
            en = row.get("en")
            if en and en not in index:
                index[en] = row
    for rows in tables.values():
        for row in rows:
            en = row.get("en")
            if en and en not in index:
                index[en] = row
    return index


def _resolve_row(en_key: str, index: dict[str, dict]) -> dict:
    row = index.get(en_key)
    if row:
        return {
            "id": row.get("id"),
            "en": row.get("en", en_key),
            "ko": row.get("ko", en_key),
            "ja": row.get("ja", en_key),
        }
    return {"id": None, "en": en_key, "ko": en_key, "ja": en_key}


def _enum_section(
    enum_cls: type[enum.IntEnum],
    en_by_value: dict[int, str],
    index: dict[str, dict],
) -> dict[str, dict]:
    section: dict[str, dict] = {}
    for member in enum_cls:
        en_key = en_by_value.get(int(member.value), member_en_key(enum_cls.__name__, member.name))
        section[str(int(member.value))] = _resolve_row(en_key, index)
    return section


def _discover_int_enums() -> list[type[enum.IntEnum]]:
    classes: list[type[enum.IntEnum]] = []
    for name in dir(game_enums):
        obj = getattr(game_enums, name)
        if (
            inspect.isclass(obj)
            and issubclass(obj, enum.IntEnum)
            and obj is not enum.IntEnum
            and obj.__module__ == game_enums.__name__
        ):
            classes.append(obj)
    return sorted(classes, key=lambda c: c.__name__)


def _en_by_value_for(enum_cls: type[enum.IntEnum]) -> dict[int, str] | None:
    name = enum_cls.__name__
    if name == "ItemAge":
        return item_age_en_keys()
    if name == "ItemType":
        return item_type_en_keys()
    if name == "Rarity":
        return rarity_en_keys()
    if name == "CurrencyType":
        return currency_en_keys()
    if name == "CombatSkill":
        return combat_skill_en_keys_from_mapping()
    return None


def build() -> dict:
    tables = _load_json(ROOT / "configs/localization/string_tables_en_ko_ja.json")
    index = _build_en_index(tables)

    out: dict = {
        "items": {},
        "pets": {},
        "mounts": {},
        "skills": {},
        "enums": {},
    }

    for key, entry in _load_json(ROOT / "configs/ItemMapping.json").items():
        out["items"][key] = _resolve_row(str(entry["Name"]), index)

    for key, entry in _load_json(ROOT / "configs/PetMapping.json").items():
        out["pets"][key] = _resolve_row(str(entry["Name"]), index)

    for key, entry in _load_json(ROOT / "configs/MountMapping.json").items():
        out["mounts"][key] = _resolve_row(str(entry["Name"]), index)

    for key, entry in _load_json(ROOT / "configs/SkillMapping.json").items():
        out["skills"][key] = _resolve_row(str(entry["Name"]), index)

    for enum_cls in _discover_int_enums():
        en_map = _en_by_value_for(enum_cls)
        if en_map is None:
            en_map = {int(m.value): member_en_key(enum_cls.__name__, m.name) for m in enum_cls}
        out["enums"][enum_cls.__name__] = _enum_section(enum_cls, en_map, index)

    return out


def main() -> int:
    data = build()
    out_path = ROOT / "configs/localization/entity_names_en_ko_ja.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    missing_enums: list[str] = []
    for enum_name, members in data["enums"].items():
        for val, row in members.items():
            if row.get("id") is None:
                missing_enums.append(f"{enum_name}[{val}]={row['en']!r}")

    print(f"Wrote {out_path}")
    print(
        f"Entries: items={len(data['items'])}, pets={len(data['pets'])}, "
        f"mounts={len(data['mounts'])}, skills={len(data['skills'])}, "
        f"enum_types={len(data['enums'])}"
    )
    if missing_enums:
        print(f"Unresolved enum members: {len(missing_enums)}")
        for line in missing_enums[:20]:
            print(" ", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
