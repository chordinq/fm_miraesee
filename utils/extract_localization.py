# utils/extract_localization.py — Unity localization bundles → en/ko/ja JSON map
"""Extract and merge Unity Localization string tables from .bundle files.

Usage:
    python utils/extract_localization.py \\
        --en path/to/localization-string-tables-english(en)_assets_all.bundle \\
        --ko path/to/localization-string-tables-korean(ko)_assets_all.bundle \\
        --ja path/to/localization-string-tables-japanese(ja)_assets_all.bundle \\
        --out configs/localization/string_tables_en_ko_ja.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import UnityPy
except ImportError as exc:  # pragma: no cover
    raise SystemExit("UnityPy required: pip install UnityPy") from exc

_LOCALE_SUFFIX = re.compile(r"_(en|ko|ja)$", re.IGNORECASE)


def _table_key(asset_name: str) -> str:
    return _LOCALE_SUFFIX.sub("", asset_name)


def _load_tables(bundle_path: Path) -> dict[str, dict[int, str]]:
    """Return {table_name: {m_Id: localized_text}}."""
    tables: dict[str, dict[int, str]] = {}
    env = UnityPy.load(str(bundle_path))
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        name = getattr(data, "m_Name", None)
        rows = getattr(data, "m_TableData", None)
        if not name or not rows:
            continue
        key = _table_key(str(name))
        bucket = tables.setdefault(key, {})
        for row in rows:
            row_id = getattr(row, "m_Id", None)
            text = getattr(row, "m_Localized", None)
            if row_id is None or text is None:
                continue
            bucket[int(row_id)] = str(text)
    return tables


def merge_locales(
    en: dict[str, dict[int, str]],
    ko: dict[str, dict[int, str]],
    ja: dict[str, dict[int, str]],
) -> dict[str, list[dict[str, Any]]]:
    all_tables = sorted(set(en) | set(ko) | set(ja))
    merged: dict[str, list[dict[str, Any]]] = {}
    for table in all_tables:
        ids = set(en.get(table, {})) | set(ko.get(table, {})) | set(ja.get(table, {}))
        entries: list[dict[str, Any]] = []
        for row_id in sorted(ids):
            entry: dict[str, Any] = {"id": row_id}
            if table in en and row_id in en[table]:
                entry["en"] = en[table][row_id]
            if table in ko and row_id in ko[table]:
                entry["ko"] = ko[table][row_id]
            if table in ja and row_id in ja[table]:
                entry["ja"] = ja[table][row_id]
            entries.append(entry)
        merged[table] = entries
    return merged


def _default_bundle_dir() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "version"
        / "2.4.0"
        / "com.hariwn.legendofcivilizations v2.4.0_antisplit"
        / "assets"
        / "aa"
        / "Android"
    )


def main(argv: list[str] | None = None) -> int:
    base = _default_bundle_dir()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--en",
        type=Path,
        default=base / "localization-string-tables-english(en)_assets_all.bundle",
    )
    parser.add_argument(
        "--ko",
        type=Path,
        default=base / "localization-string-tables-korean(ko)_assets_all.bundle",
    )
    parser.add_argument(
        "--ja",
        type=Path,
        default=base / "localization-string-tables-japanese(ja)_assets_all.bundle",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "configs" / "localization" / "string_tables_en_ko_ja.json",
    )
    args = parser.parse_args(argv)

    for label, path in ("en", args.en), ("ko", args.ko), ("ja", args.ja):
        if not path.is_file():
            print(f"Missing {label} bundle: {path}", file=sys.stderr)
            return 1

    print("Loading en...", flush=True)
    en_tables = _load_tables(args.en)
    print("Loading ko...", flush=True)
    ko_tables = _load_tables(args.ko)
    print("Loading ja...", flush=True)
    ja_tables = _load_tables(args.ja)

    merged = merge_locales(en_tables, ko_tables, ja_tables)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", encoding="utf-8") as f:
        json.dump(merged, f, ensure_ascii=False, indent=2)

    total = sum(len(v) for v in merged.values())
    print(f"Wrote {args.out}")
    print(f"Tables: {len(merged)}, entries: {total}")
    for table in sorted(merged):
        n = len(merged[table])
        full = sum(1 for e in merged[table] if "en" in e and "ko" in e and "ja" in e)
        print(f"  {table}: {n} rows ({full} with en+ko+ja)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
