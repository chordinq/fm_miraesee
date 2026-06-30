#!/usr/bin/env python3
"""Sync config/*_Mapping.json localization IDs from assets/localizations Shared Data."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOC = ROOT / "assets" / "localizations"
CONFIG = ROOT / "config"
SKINS_LIBRARY = ROOT / "core_test" / "_sgc_26_6_30" / "parsed" / "SkinsLibrary.json"


def load_shared_keys() -> dict[str, dict[str, int]]:
    tables: dict[str, dict[str, int]] = {}
    for path in LOC.glob("* Shared Data.json"):
        table = path.name.replace(" Shared Data.json", "")
        data = json.loads(path.read_text(encoding="utf-8"))
        tables[table] = {entry["m_Key"]: int(entry["m_Id"]) for entry in data.get("m_Entries", [])}
    return tables


def _desc_lookup_key(entry_key: str, file_name: str, shared: dict[str, dict[str, int]]) -> str | None:
    table = shared.get(file_name, {})
    for candidate in (f"{entry_key}Desc", f"{entry_key}Description"):
        if candidate in table:
            return candidate
    return None


def normalize_mapping_loc_blocks(obj: object, shared: dict[str, dict[str, int]]) -> bool:
    changed = False
    if isinstance(obj, dict):
        for block_name in ("Localization", "DescLocalization"):
            block = obj.get(block_name)
            if not isinstance(block, list):
                continue
            for loc in block:
                if not isinstance(loc, dict):
                    continue
                loc_id = loc.pop("id", None)
                if loc_id is not None and "Id" not in loc:
                    loc["Id"] = loc_id
                    changed = True
                file_name = loc.get("File", "")
                entry_key = obj.get("Key")
                if not entry_key or file_name not in shared:
                    continue
                if block_name == "DescLocalization":
                    lookup_key = _desc_lookup_key(entry_key, file_name, shared)
                else:
                    lookup_key = entry_key if entry_key in shared[file_name] else None
                if lookup_key is None:
                    continue
                new_id = shared[file_name][lookup_key]
                if loc.get("Id") != new_id:
                    loc["Id"] = new_id
                    changed = True
0        for value in obj.values():
            if normalize_mapping_loc_blocks(value, shared):
                changed = True
    elif isinstance(obj, list):
        for item in obj:
            if normalize_mapping_loc_blocks(item, shared):
                changed = True
    return changed


def skin_key(base_set_id: str, skin_type: str) -> str:
    prefix = base_set_id[:-3] if base_set_id.endswith("Set") else base_set_id
    return f"{prefix}_{skin_type}"


def build_skins_mapping(shared: dict[str, dict[str, int]]) -> dict[str, dict]:
    if not SKINS_LIBRARY.exists():
        skins_library = json.loads((ROOT / "assets" / "game_configs" / "SkinsLibrary.json").read_text())
    else:
        skins_library = json.loads(SKINS_LIBRARY.read_text(encoding="utf-8"))

    skins_table = shared.get("Skins", {})
    out: dict[str, dict] = {}
    missing: list[str] = []

    for row in skins_library.values():
        skin_id = row["SkinId"]
        skin_type = skin_id["Type"]
        idx = int(skin_id["Idx"])
        base_set = row.get("BaseSetId") or ""
        key = skin_key(base_set, skin_type) if base_set else f"{skin_type}_{idx}"
        loc_id = skins_table.get(key)
        if loc_id is None:
            for candidate_key, candidate_id in skins_table.items():
                if candidate_key.endswith(f"_{skin_type}") and candidate_key.lower().startswith(
                    base_set.replace("Set", "").lower()
                ):
                    key = candidate_key
                    loc_id = candidate_id
                    break
        if loc_id is None:
            missing.append(f"{base_set}/{skin_type}/{idx} -> {key}")
            continue
        map_key = f"{skin_type}_{idx}" if not base_set else f"{base_set}_{skin_type}_{idx}"
        out[map_key] = {
            "Key": key,
            "Localization": [{"File": "Skins", "Id": loc_id}],
            "SkinType": skin_type,
            "Idx": idx,
            "BaseSetId": base_set,
        }

    if missing:
        print(f"Skins mapping: {len(missing)} unmatched keys")
        for line in missing[:20]:
            print(" ", line)
    return out


def main() -> None:
    shared = load_shared_keys()

    for path in sorted(CONFIG.glob("*_Mapping.json")):
        if path.stat().st_size == 0:
            if path.name == "Skins_Mapping.json":
                mapping = build_skins_mapping(shared)
                path.write_text(json.dumps(mapping, indent="\t") + "\n", encoding="utf-8")
                print(f"WROTE {path.name}: {len(mapping)} entries")
            continue
        mapping = json.loads(path.read_text(encoding="utf-8"))
        if normalize_mapping_loc_blocks(mapping, shared):
            path.write_text(json.dumps(mapping, indent="\t") + "\n", encoding="utf-8")
            print(f"UPDATED {path.name}")
        else:
            print(f"OK {path.name}")

    skins_path = CONFIG / "Skins_Mapping.json"
    if skins_path.stat().st_size == 0 or skins_path.name not in [p.name for p in CONFIG.glob("*_Mapping.json")]:
        pass
    elif skins_path.stat().st_size > 2:
        mapping = json.loads(skins_path.read_text(encoding="utf-8"))
        if normalize_mapping_loc_blocks(mapping, shared):
            skins_path.write_text(json.dumps(mapping, indent="\t") + "\n", encoding="utf-8")
            print("UPDATED Skins_Mapping.json")


if __name__ == "__main__":
    main()
