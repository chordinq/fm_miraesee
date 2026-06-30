#!/usr/bin/env python3
"""MCA! archive -> decompressed .mpc, then .mpc -> assets/game_configs JSON."""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from .dump_schema import get_registry
from .extract_shared_config import extract_archive
from .json_convert import decode_mpc
from .paths import GAME_CONFIGS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SharedGameConfig and decode to JSON")
    parser.add_argument("input", type=Path, help="SharedGameConfig binary (.hex or raw)")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="directory for extracted .mpc blobs (default: input parent / mpc)",
    )
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=GAME_CONFIGS_DIR,
        help=f"JSON output directory (default: {GAME_CONFIGS_DIR})",
    )
    parser.add_argument("--dump", type=Path, help="path to dump.cs")
    parser.add_argument("--mpc-only", action="store_true", help="only extract .mpc, skip JSON")
    args = parser.parse_args()

    mpc_dir = args.output or (args.input.parent / "mpc")
    mpc_dir.mkdir(parents=True, exist_ok=True)

    extract_archive(args.input.read_bytes(), mpc_dir)

    if args.mpc_only:
        return

    registry = get_registry(args.dump)
    args.json_dir.mkdir(parents=True, exist_ok=True)

    ok = 0
    failed: list[str] = []
    for mpc in sorted(mpc_dir.glob("*.mpc")):
        entry_name = mpc.stem
        try:
            result = decode_mpc(mpc.read_bytes(), entry_name, registry)
            out = args.json_dir / f"{entry_name}.json"
            out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(f"OK {entry_name} -> {out}")
            ok += 1
        except Exception as exc:
            failed.append(f"{entry_name}: {exc}")
            print(f"FAIL {entry_name}: {exc}")
            traceback.print_exc()

    total = len(list(mpc_dir.glob("*.mpc")))
    print(f"\ndone: {ok} ok, {len(failed)} failed, {total} total -> {args.json_dir}")
    if failed:
        print("failures:")
        for line in failed:
            print(" ", line)


if __name__ == "__main__":
    main()
