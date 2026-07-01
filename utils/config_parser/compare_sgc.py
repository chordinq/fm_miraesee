#!/usr/bin/env python3
"""Decode SharedGameConfig hex/binary and diff against assets/game_configs."""

from __future__ import annotations

import argparse
import binascii
import json
import sys
import traceback
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_HEX = PROJECT_ROOT / "data" / "sgc_26_7_01" / "SharedGameConfigHex.txt"
DEFAULT_OUT = PROJECT_ROOT / "data" / "sgc_26_7_01" / "json"
DEFAULT_BASELINE = PROJECT_ROOT / "assets" / "game_configs"
DEFAULT_DUMP = PROJECT_ROOT / "data" / "dump.cs"


def load_archive_bytes(path: Path) -> bytes:
	raw = path.read_bytes()
	if not raw:
		raise ValueError(f"{path} is empty — save the hex file in your editor first (Ctrl+S)")
	if raw[:4] == b"MCA!":
		return raw
	text = raw.decode("ascii", errors="ignore").strip().replace("\n", "").replace("\r", "").replace(" ", "")
	if not text:
		raise ValueError(f"{path} has no hex or binary content")
	try:
		return binascii.unhexlify(text)
	except binascii.Error as exc:
		raise ValueError(f"{path} is not valid hex or MCA! binary: {exc}") from exc


def decode_archive(archive: bytes, out_dir: Path, dump_path: Path) -> tuple[int, list[str]]:
	sys.path.insert(0, str(PROJECT_ROOT))
	from utils.config_parser.dump_schema import get_registry
	from utils.config_parser.extract_shared_config import extract_archive
	from utils.config_parser.json_convert import decode_mpc

	mpc_dir = out_dir.parent / "mpc"
	mpc_dir.mkdir(parents=True, exist_ok=True)
	out_dir.mkdir(parents=True, exist_ok=True)

	extract_archive(archive, mpc_dir)
	registry = get_registry(dump_path)

	ok = 0
	failed: list[str] = []
	for mpc in sorted(mpc_dir.glob("*.mpc")):
		entry_name = mpc.stem
		try:
			result = decode_mpc(mpc.read_bytes(), entry_name, registry)
			(out_dir / f"{entry_name}.json").write_text(
				json.dumps(result, indent=2) + "\n",
				encoding="utf-8",
			)
			ok += 1
		except Exception as exc:
			failed.append(f"{entry_name}: {exc}")
			traceback.print_exc()
	return ok, failed


def _deep_diff(a: Any, b: Any, path: str = "") -> list[str]:
	changes: list[str] = []
	if type(a) != type(b):
		changes.append(f"{path or '$'}: type {type(a).__name__} -> {type(b).__name__}")
		return changes
	if isinstance(a, dict):
		all_keys = sorted(set(a) | set(b), key=str)
		for key in all_keys:
			sub = f"{path}.{key}" if path else str(key)
			if key not in a:
				changes.append(f"+ {sub}")
			elif key not in b:
				changes.append(f"- {sub}")
			else:
				changes.extend(_deep_diff(a[key], b[key], sub))
		return changes
	if isinstance(a, list):
		if len(a) != len(b):
			changes.append(f"{path}: list len {len(a)} -> {len(b)}")
		for index, (left, right) in enumerate(zip(a, b, strict=False)):
			changes.extend(_deep_diff(left, right, f"{path}[{index}]"))
		return changes
	if a != b:
		changes.append(f"~ {path or '$'}: {a!r} -> {b!r}")
	return changes


def compare_dirs(new_dir: Path, baseline_dir: Path, *, max_samples: int = 8) -> dict[str, Any]:
	new_files = {p.name for p in new_dir.glob("*.json")}
	base_files = {p.name for p in baseline_dir.glob("*.json")}

	report: dict[str, Any] = {
		"only_in_new": sorted(new_files - base_files),
		"only_in_baseline": sorted(base_files - new_files),
		"identical": [],
		"changed": {},
		"failed_read": [],
	}

	for name in sorted(new_files & base_files):
		try:
			new_data = json.loads((new_dir / name).read_text(encoding="utf-8"))
			base_data = json.loads((baseline_dir / name).read_text(encoding="utf-8"))
		except Exception as exc:
			report["failed_read"].append(f"{name}: {exc}")
			continue
		if new_data == base_data:
			report["identical"].append(name)
			continue
		diff = _deep_diff(base_data, new_data)
		report["changed"][name] = {
			"change_count": len(diff),
			"samples": diff[:max_samples],
		}

	return report


def main() -> None:
	parser = argparse.ArgumentParser(description="Extract SGC hex and diff game_configs")
	parser.add_argument("input", nargs="?", type=Path, default=DEFAULT_HEX)
	parser.add_argument("-o", "--output", type=Path, default=DEFAULT_OUT)
	parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
	parser.add_argument("--dump", type=Path, default=DEFAULT_DUMP)
	parser.add_argument("--compare-only", action="store_true")
	args = parser.parse_args()

	if not args.compare_only:
		archive = load_archive_bytes(args.input)
		if archive[:4] != b"MCA!":
			raise SystemExit("decoded bytes do not start with MCA!")
		print(f"archive: {len(archive)} bytes, magic MCA!")
		ok, failed = decode_archive(archive, args.output, args.dump)
		total = len(list((args.output.parent / "mpc").glob("*.mpc")))
		print(f"decoded: {ok}/{total} ok, {len(failed)} failed -> {args.output}")
		for line in failed:
			print(" FAIL", line)

	report = compare_dirs(args.output, args.baseline)
	print("\n=== compare vs assets/game_configs ===")
	print(f"identical: {len(report['identical'])}")
	print(f"changed:   {len(report['changed'])}")
	print(f"only new:  {len(report['only_in_new'])} {report['only_in_new']}")
	print(f"only old:  {len(report['only_in_baseline'])} {report['only_in_baseline']}")
	if report["changed"]:
		print("\nchanged files (sample diffs):")
		for name, info in sorted(report["changed"].items()):
			print(f"  {name}: {info['change_count']} path(s)")
			for sample in info["samples"]:
				print(f"    {sample}")
			if info["change_count"] > len(info["samples"]):
				print(f"    ... +{info['change_count'] - len(info['samples'])} more")

	summary_path = args.output.parent / "diff_report.json"
	summary_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
	print(f"\nfull report: {summary_path}")


if __name__ == "__main__":
	main()
