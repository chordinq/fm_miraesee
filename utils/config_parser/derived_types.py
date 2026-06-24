"""MetaSerializableDerived type id -> class name (from dump.cs)."""

from __future__ import annotations

import re
from pathlib import Path

_CACHE: dict[tuple[str, int], str] | None = None


def load_derived_types(dump_path: Path) -> dict[tuple[str, int], str]:
    global _CACHE
    if _CACHE is not None:
        return _CACHE
    text = dump_path.read_text(encoding="utf-8", errors="ignore")
    mapping: dict[tuple[str, int], str] = {}
    for m in re.finditer(
        r"\[MetaSerializableDerived\((\d+)\)\]\s*public class (\w+)\s*:\s*(\w+)",
        text,
    ):
        mapping[(m.group(3), int(m.group(1)))] = m.group(2)
    _CACHE = mapping
    return mapping


def resolve_type_name(base: str, disc: int, dump_path: Path) -> str:
    return load_derived_types(dump_path).get((base, disc), f"Derived{disc}")
