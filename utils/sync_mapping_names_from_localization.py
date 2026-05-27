# utils/sync_mapping_names_from_localization.py — align *Mapping.json Name with string_tables en
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES_PATH = ROOT / "configs/localization/string_tables_en_ko_ja.json"

# Old Name in mapping -> canonical en from string_tables_en_ko_ja.json
_CORRECTIONS: dict[str, dict[str, str]] = {
    "configs/ItemMapping.json": {
        "BearPaw": "Bearpaw",
        "Circleof Pain": "Circle of Pain",
        "Gripof Torment": "Grip of Torment",
        "Siren Song": "Siren's Song",
        "Wizard Hat": "Wizard's Hat",
    },
    "configs/MountMapping.json": {
        "One Wheel Droidx": "Droid",
    },
    "configs/SkillMapping.json": {
        "Rain of Arrows": "Arrow Rain",
        "Shuriken": "Shurikens",
    },
}

_TABLE_FOR_FILE = {
    "configs/ItemMapping.json": "Items",
    "configs/PetMapping.json": "Pets",
    "configs/MountMapping.json": "Pets",
    "configs/SkillMapping.json": "Skills",
}


def _load(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _save(path: Path, data: dict) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent="\t")
        f.write("\n")


def _en_index(tables: dict, table: str) -> set[str]:
    return {row["en"] for row in tables.get(table, []) if row.get("en")}


def sync_file(rel_path: str, tables: dict) -> list[str]:
    path = ROOT / rel_path
    mapping = _load(path)
    table = _TABLE_FOR_FILE[rel_path]
    valid = _en_index(tables, table)
    corrections = _CORRECTIONS.get(rel_path, {})
    changes: list[str] = []

    for key, entry in mapping.items():
        name = str(entry.get("Name", ""))
        if name in valid:
            continue
        new_name = corrections.get(name)
        if not new_name or new_name not in valid:
            raise ValueError(
                f"{rel_path} [{key}] Name={name!r} not in string_tables {table} "
                f"and no valid correction"
            )
        entry["Name"] = new_name
        changes.append(f"{key}: {name!r} -> {new_name!r}")

    if changes:
        _save(path, mapping)
    return changes


def sync_auto_item_names(item_mapping: dict) -> list[str]:
    auto_path = ROOT / "configs/AutoItemMapping.json"
    if not auto_path.is_file():
        return []
    auto = _load(auto_path)
    changes: list[str] = []
    for key, entry in auto.items():
        item = item_mapping.get(key)
        if not item:
            continue
        canonical = str(item["Name"])
        old = entry.get("ItemName")
        if old and old != canonical:
            entry["ItemName"] = canonical
            changes.append(f"{key}: ItemName {old!r} -> {canonical!r}")
    if changes:
        _save(auto_path, auto)
    return changes


def main() -> int:
    tables = _load(TABLES_PATH)
    all_changes: list[str] = []

    item_mapping = _load(ROOT / "configs/ItemMapping.json")
    for rel in _TABLE_FOR_FILE:
        if rel == "configs/ItemMapping.json":
            ch = sync_file(rel, tables)
            item_mapping = _load(ROOT / "configs/ItemMapping.json")
        else:
            ch = sync_file(rel, tables)
        all_changes.extend(f"{rel}: {c}" for c in ch)

    auto_ch = sync_auto_item_names(item_mapping)
    all_changes.extend(f"AutoItemMapping: {c}" for c in auto_ch)

    if not all_changes:
        print("No mapping name changes needed.")
    else:
        print("Updated:")
        for line in all_changes:
            print(" ", line)

    # Verify all mapping names exist in string tables
    for rel, table in _TABLE_FOR_FILE.items():
        mapping = _load(ROOT / rel)
        valid = _en_index(tables, table)
        bad = [f"{k}={v['Name']!r}" for k, v in mapping.items() if v["Name"] not in valid]
        if bad:
            print(f"VERIFY FAIL {rel}:", bad[:10])
            return 1
    print("Verify OK: all mapping names exist in string_tables.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
