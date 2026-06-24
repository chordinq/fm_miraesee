#!/usr/bin/env python3
"""MCA! archive -> decompressed .mpc, then .mpc -> JSON (configs with registered decoders)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .extract_shared_config import extract_archive
from .schemas import DECODERS


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SharedGameConfig and decode to JSON")
    parser.add_argument("input", type=Path, help="SharedGameConfig binary (.hex or raw)")
    parser.add_argument("-o", "--output", type=Path, required=True, help="output directory")
    parser.add_argument("--mpc-only", action="store_true", help="only extract .mpc, skip JSON")
    args = parser.parse_args()

    mpc_dir = args.output / "mpc"
    json_dir = args.output / "json"
    mpc_dir.mkdir(parents=True, exist_ok=True)
    if not args.mpc_only:
        json_dir.mkdir(parents=True, exist_ok=True)

    extract_archive(args.input.read_bytes(), mpc_dir)

    if args.mpc_only:
        return

    decoded = 0
    for mpc in sorted(mpc_dir.glob("*.mpc")):
        decoder = DECODERS.get(mpc.stem)
        if not decoder:
            continue
        result = decoder(mpc.read_bytes())
        out = json_dir / f"{mpc.stem}.json"
        out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
        decoded += 1
        print(f"{mpc.name} -> {out.name}")

    print(f"decoded {decoded} / {len(list(mpc_dir.glob('*.mpc')))} mpc files")


if __name__ == "__main__":
    main()
