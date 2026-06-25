from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from utils.dump.parser import parse_dump_text


def show_hidden(path: Path, label: str):
    snap = parse_dump_text(path.read_text(encoding="utf-8"))
    print(f"=== {label} hidden levels ({len(snap.hidden_levels)}) ===")
    for e in snap.hidden_levels:
        print(f"  type={e.item_type} age={e.age} level={e.level}")


def show_equipment(path: Path, label: str):
    snap = parse_dump_text(path.read_text(encoding="utf-8"))
    print(f"=== {label} equipment ({len(snap.equipment)}) ===")
    for e in snap.equipment:
        print(f"  slot={e.slot} type={e.item_type} level={e.level}")


base = Path(__file__).resolve().parent
for name, label in [("_old_dump.txt", "OLD"), ("test_user_dump.txt", "NEW")]:
    show_hidden(base / name, label)
    show_equipment(base / name, label)
    print()
