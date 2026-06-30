#!/usr/bin/env python3
"""Batch-decode all .mpc configs to JSON."""

from __future__ import annotations

import argparse
import json
import traceback
from pathlib import Path

from .dump_schema import get_registry
from .json_convert import decode_mpc
from .paths import GAME_CONFIGS_DIR


def main() -> None:
    parser = argparse.ArgumentParser(description="Decode all .mpc configs to JSON")
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=Path(r"c:\Users\chord\Downloads\dumped_configs_full"),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=GAME_CONFIGS_DIR,
    )
    parser.add_argument("--dump", type=Path, help="path to dump.cs")
    args = parser.parse_args()

    registry = get_registry(args.dump)
    args.output.mkdir(parents=True, exist_ok=True)

    ok = 0
    failed: list[str] = []
    for mpc in sorted(args.input.glob("*.mpc")):
        entry_name = mpc.stem
        try:
            result = decode_mpc(mpc.read_bytes(), entry_name, registry)
            out = args.output / f"{entry_name}.json"
            out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
            print(f"OK {entry_name}")
            ok += 1
        except Exception as exc:
            failed.append(f"{entry_name}: {exc}")
            print(f"FAIL {entry_name}: {exc}")
            traceback.print_exc()

    print(f"\ndone: {ok} ok, {len(failed)} failed, {len(list(args.input.glob('*.mpc')))} total")
    if failed:
        print("failures:")
        for line in failed:
            print(" ", line)


if __name__ == "__main__":
    main()
