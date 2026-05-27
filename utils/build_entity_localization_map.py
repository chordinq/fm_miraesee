# utils/build_entity_localization_map.py — mapping JSON keys → en/ko/ja from string tables
"""Build configs/localization/entity_names_en_ko_ja.json from *Mapping.json + string tables."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

_AGE_EN: dict[int, str] = {
    0: "Primitive",
    1: "Medieval",
    2: "Early-Modern",
    3: "Modern",
    4: "Space",
    5: "Interstellar",
    6: "Multiverse",
    7: "Quantum",
    8: "Underworld",
    9: "Divine",
}


def _load_json(path: Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def _table_index(tables: dict, table: str) -> dict[str, dict]:
    return {row["en"]: row for row in tables.get(table, []) if row.get("en")}


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


def build() -> dict:
    tables = _load_json(ROOT / "configs/localization/string_tables_en_ko_ja.json")
    items_i = _table_index(tables, "Items")
    pets_i = _table_index(tables, "Pets")
    skills_i = _table_index(tables, "Skills")
    forge_i = _table_index(tables, "Forge")

    out: dict = {
        "items": {},
        "pets": {},
        "mounts": {},
        "skills": {},
        "ages": {},
    }

    for key, entry in _load_json(ROOT / "configs/ItemMapping.json").items():
        en = str(entry["Name"])
        out["items"][key] = _resolve_row(en, items_i)

    for key, entry in _load_json(ROOT / "configs/PetMapping.json").items():
        en = str(entry["Name"])
        out["pets"][key] = _resolve_row(en, pets_i)

    for key, entry in _load_json(ROOT / "configs/MountMapping.json").items():
        en = str(entry["Name"])
        out["mounts"][key] = _resolve_row(en, pets_i)

    for key, entry in _load_json(ROOT / "configs/SkillMapping.json").items():
        en = str(entry["Name"])
        out["skills"][key] = _resolve_row(en, skills_i)

    for age, en in _AGE_EN.items():
        out["ages"][str(age)] = _resolve_row(en, forge_i)

    return out


def main() -> int:
    data = build()
    out_path = ROOT / "configs/localization/entity_names_en_ko_ja.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    missing = []
    for group in ("items", "pets", "mounts", "skills"):
        for key, row in data[group].items():
            if row["en"] == row["ko"] == row["ja"] and row.get("id") is None:
                missing.append(f"{group}:{key}:{row['en']}")
    print(f"Wrote {out_path}")
    print(f"Entries: items={len(data['items'])}, pets={len(data['pets'])}, "
          f"mounts={len(data['mounts'])}, skills={len(data['skills'])}, ages={len(data['ages'])}")
    if missing:
        print(f"Unresolved (fallback English): {len(missing)}")
        for line in missing[:10]:
            print(" ", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
