import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOC = ROOT / "assets/localizations"
CONFIG = ROOT / "config"

locales = set()
for p in LOC.glob("*.json"):
    if "(" in p.name and ").json" in p.name:
        m = re.search(r"\(([^)]+)\)\.json$", p.name)
        if m:
            code = m.group(1).split()[-1] if " " in m.group(1) else m.group(1)
            locales.add(code)

table_langs: dict[str, set[str]] = {}
for p in LOC.glob("*_*.json"):
    if " Shared Data" in p.name:
        continue
    parts = p.stem.rsplit("_", 1)
    if len(parts) == 2:
        table, lang = parts
        table_langs.setdefault(table, set()).add(lang)

print("Locale definition files:", sorted(locales))
all_langs = sorted(set().union(*table_langs.values()))
print("All table langs:", all_langs)

shared_ids: dict[str, dict[str, str]] = {}
shared_keys: dict[tuple[str, str], str] = {}
for p in LOC.glob("* Shared Data.json"):
    table = p.name.replace(" Shared Data.json", "")
    data = json.loads(p.read_text(encoding="utf-8"))
    shared_ids[table] = {str(e["m_Id"]): e["m_Key"] for e in data.get("m_Entries", [])}
    for e in data.get("m_Entries", []):
        shared_keys[(table, e["m_Key"])] = str(e["m_Id"])

stale_mapping: list[str] = []
for mp in CONFIG.glob("*_Mapping.json"):
    if mp.stat().st_size == 0:
        stale_mapping.append(f"EMPTY: {mp.name}")
        continue
    m = json.loads(mp.read_text(encoding="utf-8"))

    def walk(obj, path=""):
        if isinstance(obj, dict):
            if "Localization" in obj and isinstance(obj["Localization"], list):
                for loc in obj["Localization"]:
                    fid = str(loc.get("Id", ""))
                    file = loc.get("File", "")
                    if file and fid not in shared_ids.get(file, {}):
                        stale_mapping.append(f"{mp.name} {path}: {file} id {fid}")
            for k, v in obj.items():
                walk(v, f"{path}.{k}" if path else k)
        elif isinstance(obj, list):
            for i, v in enumerate(obj):
                walk(v, f"{path}[{i}]")

    walk(m)

print(f"\nMapping issues: {len(stale_mapping)}")
for line in stale_mapping[:40]:
    print(" ", line)

all_shared: dict[str, tuple[str, str]] = {}
for table, m in shared_ids.items():
    for i, k in m.items():
        all_shared[i] = (table, k)

ids: set[str] = set()
for path in [ROOT / "ui", ROOT / "core/game_logic/number_format.py"]:
    if path.is_dir():
        for f in path.rglob("*"):
            if f.suffix in (".qml", ".py"):
                ids.update(re.findall(r'"([0-9]{10,})"', f.read_text(encoding="utf-8", errors="ignore")))
    else:
        ids.update(re.findall(r'"([0-9]{10,})"', path.read_text(encoding="utf-8", errors="ignore")))

missing = sorted(i for i in ids if not i.startswith("1000000000") and i not in all_shared)
print(f"\nHardcoded IDs not in Shared Data: {len(missing)}")
for i in missing:
    print(f"  {i}")

lang_in_ui = {"en", "de", "ja", "ko", "fr", "es", "pt-BR", "it", "ru", "tr-TR"}
new_langs = set(all_langs) - lang_in_ui
print("\nLangs in assets but not LanguageSettingsView:", sorted(new_langs))
missing_files = []
for lang in lang_in_ui:
    if lang not in table_langs.get("General", set()):
        missing_files.append(f"General_{lang}")
print("Missing General tables for UI langs:", missing_files)
