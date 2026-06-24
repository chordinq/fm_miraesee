#!/usr/bin/env python3
"""Convert decompressed .mpc blobs to JSON (step 2)."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .schemas import DECODERS

DECODERS = {f"{name}.mpc": fn for name, fn in DECODERS.items()}


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode .mpc config blob to JSON")
    parser.add_argument("input", type=Path, help=".mpc file or directory")
    parser.add_argument("-o", "--output", type=Path, help="output .json path or directory")
    args = parser.parse_args()

    if args.input.is_dir():
        out_dir = args.output or args.input
        out_dir.mkdir(parents=True, exist_ok=True)
        for mpc in sorted(args.input.glob("*.mpc")):
            decoder = DECODERS.get(mpc.name)
            if not decoder:
                continue
            result = decoder(mpc.read_bytes())
            json_path = out_dir / mpc.name.replace(".mpc", ".json")
            json_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(f"{mpc.name} -> {json_path.name}")
        return

    decoder = DECODERS.get(args.input.name)
    if not decoder:
        raise SystemExit(f"no decoder for {args.input.name}")

    result = decoder(args.input.read_bytes())
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
        print(f"wrote {args.output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
