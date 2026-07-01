"""MetaSerializableDerived type id -> class name (from dump.cs)."""

from __future__ import annotations

import re
from pathlib import Path

DEFAULT_DUMP = Path(__file__).resolve().parents[2] / "data" / "dump.cs"
_CACHE: dict[str, dict[tuple[str, int], str]] = {}


def load_derived_types(dump_path: Path | None = None) -> dict[tuple[str, int], str]:
    path = (dump_path or DEFAULT_DUMP).resolve()
    key = str(path)
    cached = _CACHE.get(key)
    if cached is not None:
        return cached
    text = path.read_text(encoding="utf-8", errors="ignore")
    mapping: dict[tuple[str, int], str] = {}
    for m in re.finditer(
        r"\[MetaSerializableDerived\((\d+)\)\]\s*public class (\w+)\s*:\s*(\w+)",
        text,
    ):
        mapping[(m.group(3), int(m.group(1)))] = m.group(2)
    _CACHE[key] = mapping
    return mapping


def resolve_type_name(base: str, disc: int, dump_path: Path | None = None) -> str:
    return load_derived_types(dump_path).get((base, disc), f"Derived{disc}")
