#!/usr/bin/env python3
"""Extract decompressed .mpc blobs from Metaplay SharedGameConfig (MCA! archive).

Based on decompiled:
  ConfigArchiveBuildUtility.ReadEntryHeader
  ConfigArchive.Load
  CompressUtil.DeflateDecompress  (raw deflate, wbits=-15)
"""

from __future__ import annotations

import argparse
import struct
import zlib
from dataclasses import dataclass
from pathlib import Path

COMPRESSION_NONE = 0
COMPRESSION_DEFLATE = 1


@dataclass
class ArchiveHeader:
    schema_version: int
    content_hash: bytes
    created_at: int
    num_entries: int


@dataclass
class EntryHeader:
    name: str
    content_hash: bytes
    compression: int
    compressed_size: int


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


def read_metaplay_string(data: bytes, offset: int, max_size: int = 0x400) -> tuple[str, int]:
    """IOReader.ReadString: varint (len<<1|unicode_flag) + utf-8 bytes."""
    val, offset = read_varint(data, offset)
    length = val >> 1
    if length > max_size:
        raise ValueError(f"entry name too long: {length}")
    name = data[offset : offset + length].decode("utf-8")
    return name, offset + length


def read_archive_header(data: bytes) -> tuple[ArchiveHeader, int]:
    if data[:4] != b"MCA!":
        raise ValueError("not an MCA! archive")
    schema_version = struct.unpack_from(">I", data, 4)[0]
    content_hash = data[8:24]
    created_at = struct.unpack_from(">Q", data, 24)[0]
    num_entries = struct.unpack_from(">I", data, 32)[0]
    return ArchiveHeader(schema_version, content_hash, created_at, num_entries), 36


def read_entry_header(data: bytes, offset: int, schema_version: int) -> tuple[EntryHeader, int]:
    name, offset = read_metaplay_string(data, offset)
    content_hash = data[offset : offset + 16]
    offset += 16
    compression = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    if schema_version < 5:
        compression = COMPRESSION_NONE
    compressed_size = struct.unpack_from(">I", data, offset)[0]
    offset += 4
    return EntryHeader(name, content_hash, compression, compressed_size), offset


def deflate_decompress(payload: bytes) -> bytes:
    return zlib.decompress(payload, wbits=-15)


def format_content_hash(raw: bytes) -> str:
    return f"{raw[:8].hex().upper()}-{raw[8:].hex().upper()}"


def extract_archive(
    data: bytes,
    output_dir: Path,
    *,
    keep_compressed: bool = False,
) -> list[EntryHeader]:
    header, offset = read_archive_header(data)
    entries: list[EntryHeader] = []

    for _ in range(header.num_entries):
        entry, offset = read_entry_header(data, offset, header.schema_version)
        entries.append(entry)

    payload_start = offset
    cur = payload_start
    output_dir.mkdir(parents=True, exist_ok=True)

    for entry in entries:
        if cur + entry.compressed_size > len(data):
            raise ValueError(f"truncated payload for {entry.name}")

        blob = data[cur : cur + entry.compressed_size]
        cur += entry.compressed_size

        if entry.compression == COMPRESSION_NONE:
            out_bytes = blob
        elif entry.compression == COMPRESSION_DEFLATE:
            out_bytes = deflate_decompress(blob)
        else:
            raise ValueError(f"unsupported compression {entry.compression} for {entry.name}")

        out_name = entry.name
        if not keep_compressed and out_name.endswith(".mpc"):
            pass
        out_path = output_dir / out_name
        out_path.write_bytes(out_bytes)

        if keep_compressed and entry.compression != COMPRESSION_NONE:
            (output_dir / f"{entry.name}.compressed").write_bytes(blob)

    if cur != len(data):
        raise ValueError(f"leftover bytes after payload: {len(data) - cur}")

    return entries


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract SharedGameConfig MCA! archive")
    parser.add_argument(
        "input",
        nargs="?",
        default="SharedGameConfig.hex",
        help="MCA archive file path",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="dumped_configs",
        help="output directory for decompressed .mpc files",
    )
    parser.add_argument(
        "--keep-compressed",
        action="store_true",
        help="also save raw compressed blobs",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    data = input_path.read_bytes()
    header, _ = read_archive_header(data)

    print(f"input: {input_path} ({len(data)} bytes)")
    print(f"schema: v{header.schema_version}")
    print(f"hash:   {format_content_hash(header.content_hash)}")
    print(f"entries: {header.num_entries}")

    entries = extract_archive(data, Path(args.output), keep_compressed=args.keep_compressed)

    none_count = sum(1 for e in entries if e.compression == COMPRESSION_NONE)
    deflate_count = sum(1 for e in entries if e.compression == COMPRESSION_DEFLATE)
    print(f"extracted {len(entries)} files -> {args.output}")
    print(f"compression: none={none_count}, deflate={deflate_count}")


if __name__ == "__main__":
    main()
