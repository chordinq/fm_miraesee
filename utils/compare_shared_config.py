#!/usr/bin/env python3
"""Compare two SharedGameConfig MCA! archives."""

from __future__ import annotations

import hashlib
import re
import struct
import sys
import zlib
from pathlib import Path

COMPRESSION_NONE = 0
COMPRESSION_DEFLATE = 1


def load_bytes(path: Path) -> bytes:
    raw = path.read_bytes()
    if raw[:4] == b"MCA!":
        return raw
    text = raw.decode("ascii", errors="ignore")
    hexstr = re.sub(r"[^0-9a-fA-F]", "", text)
    return bytes.fromhex(hexstr)


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    val = 0
    shift = 0
    while offset < len(data):
        b = data[offset]
        offset += 1
        val |= (b & 0x7F) << shift
        if (b & 0x80) == 0:
            break
        shift += 7
    return val, offset


def read_string(data: bytes, offset: int) -> tuple[str, int]:
    val, offset = read_varint(data, offset)
    length = val >> 1
    name = data[offset : offset + length].decode("utf-8")
    return name, offset + length


def parse_archive(data: bytes) -> dict:
    if data[:4] != b"MCA!":
        raise ValueError("not an MCA! archive")

    schema = struct.unpack_from(">I", data, 4)[0]
    content_hash = data[8:24]
    created_at = struct.unpack_from(">Q", data, 24)[0]
    num_entries = struct.unpack_from(">I", data, 32)[0]
    offset = 36
    entries: list[dict] = []

    for idx in range(num_entries):
        if offset >= len(data):
            entries.append({"name": f"<truncated-at-entry-{idx}>", "truncated_header": True})
            break
        try:
            name, offset = read_string(data, offset)
        except Exception:
            entries.append({"name": f"<truncated-at-entry-{idx}>", "truncated_header": True})
            break
        if offset + 24 > len(data):
            entries.append({"name": name, "truncated_header": True})
            break
        entry_hash = data[offset : offset + 16]
        offset += 16
        compression = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        if schema < 5:
            compression = COMPRESSION_NONE
        csize = struct.unpack_from(">I", data, offset)[0]
        offset += 4
        entries.append(
            {
                "name": name,
                "hash": entry_hash,
                "compression": compression,
                "csize": csize,
            }
        )

    payload_start = offset
    cur = payload_start
    for entry in entries:
        if entry.get("truncated_header"):
            continue
        if cur + entry["csize"] > len(data):
            entry["truncated"] = True
            entry["payload"] = data[cur:]
            cur = len(data)
            break

        blob = data[cur : cur + entry["csize"]]
        cur += entry["csize"]
        entry["payload"] = blob

        if entry["compression"] == COMPRESSION_DEFLATE:
            try:
                dec = zlib.decompress(blob, wbits=-15)
            except zlib.error as exc:
                dec = None
                entry["decompress_error"] = str(exc)
        else:
            dec = blob

        entry["decompressed"] = dec
        if dec is not None:
            entry["decompressed_size"] = len(dec)
            entry["decompressed_md5"] = hashlib.md5(dec).hexdigest()

    return {
        "schema": schema,
        "content_hash": content_hash,
        "created_at": created_at,
        "num_entries": num_entries,
        "entries": entries,
        "total_size": len(data),
        "payload_end": cur,
        "truncated": cur < len(data) or any(e.get("truncated") for e in entries),
    }


def fmt_hash(raw: bytes) -> str:
    return f"{raw[:8].hex().upper()}-{raw[8:].hex().upper()}"


def compare(old: dict, new: dict) -> dict:
    old_map = {e["name"]: e for e in old["entries"] if not e.get("truncated_header")}
    new_map = {e["name"]: e for e in new["entries"] if not e.get("truncated_header")}
    only_old = sorted(set(old_map) - set(new_map))
    only_new = sorted(set(new_map) - set(old_map))
    common = sorted(set(old_map) & set(new_map))

    unchanged: list[str] = []
    changed: list[str] = []
    for name in common:
        o = old_map[name]
        n = new_map[name]
        if o["hash"] == n["hash"] and o["csize"] == n["csize"]:
            unchanged.append(name)
        else:
            changed.append(name)

    return {
        "only_old": only_old,
        "only_new": only_new,
        "unchanged": unchanged,
        "changed": changed,
        "old_map": old_map,
        "new_map": new_map,
    }


def main() -> None:
    old_path = Path(sys.argv[1] if len(sys.argv) > 1 else r"c:\Users\chord\Downloads\SharedGameConfig.hex")
    new_path = Path(
        sys.argv[2] if len(sys.argv) > 2 else r"c:\Users\chord\Downloads\SharedGameConfig_4_5_0.hex"
    )

    old_data = load_bytes(old_path)
    new_data = load_bytes(new_path)
    old = parse_archive(old_data)
    new = parse_archive(new_data)

    print("=== SharedGameConfig.hex (baseline) ===")
    print(f"path: {old_path}")
    print(f"bytes: {old['total_size']}")
    print(f"schema: v{old['schema']}")
    print(f"content_hash: {fmt_hash(old['content_hash'])}")
    print(f"created_at: {old['created_at']}")
    print(f"entries: {old['num_entries']}")
    print(f"payload_end: {old['payload_end']}")

    print("\n=== SharedGameConfig_4_5_0.hex ===")
    print(f"path: {new_path}")
    print(f"bytes: {new['total_size']}")
    print(f"schema: v{new['schema']}")
    print(f"content_hash: {fmt_hash(new['content_hash'])}")
    print(f"created_at: {new['created_at']}")
    print(f"entries (header): {new['num_entries']}")
    print(f"entries (parsed): {len(new['entries'])}")
    print(f"payload_end: {new['payload_end']}")
    if new["truncated"]:
        print("WARNING: 4_5_0 archive data is TRUNCATED (incomplete dump)")

    print("\n=== Header diff ===")
    print(f"same content_hash: {old['content_hash'] == new['content_hash']}")
    print(f"same created_at:   {old['created_at'] == new['created_at']}")
    print(f"same entry count:  {old['num_entries'] == new['num_entries']}")

    result = compare(old, new)
    print("\n=== Entry list diff ===")
    print(f"only in baseline: {len(result['only_old'])}")
    print(f"only in 4_5_0:    {len(result['only_new'])}")
    print(f"common:           {len(result['unchanged']) + len(result['changed'])}")
    print(f"unchanged hash:   {len(result['unchanged'])}")
    print(f"changed hash:     {len(result['changed'])}")

    if result["only_new"]:
        print("\nAdded in 4_5_0:")
        for name in result["only_new"]:
            print(f"  + {name}")

    if result["only_old"]:
        print(f"\nMissing from 4_5_0 dump ({len(result['only_old'])} total):")
        for name in result["only_old"][:10]:
            print(f"  - {name}")
        if len(result["only_old"]) > 10:
            print(f"  ... and {len(result['only_old']) - 10} more")

    if result["changed"]:
        print("\nChanged entries (entry content hash differs):")
        for name in result["changed"]:
            o = result["old_map"][name]
            n = result["new_map"][name]
            print(f"  * {name}")
            print(f"      old: hash={o['hash'].hex()} csize={o['csize']} dec={o.get('decompressed_size')}")
            print(f"      new: hash={n['hash'].hex()} csize={n['csize']} dec={n.get('decompressed_size')}")
            if o.get("decompressed_md5") and n.get("decompressed_md5"):
                print(f"      md5: {o['decompressed_md5']} -> {n['decompressed_md5']}")


if __name__ == "__main__":
    main()
