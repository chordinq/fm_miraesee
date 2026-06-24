"""Metaplay fixed-point F64 (Raw i64, 32 fractional bits)."""

from __future__ import annotations

import struct

FRACTIONAL_BITS = 32
SCALE = 1 << FRACTIONAL_BITS


def f64_from_raw(raw: int) -> float:
    if raw >= 0x8000000000000000:
        raw -= 1 << 64
    return raw / SCALE


def read_f64(data: bytes, offset: int) -> tuple[float, int]:
    raw = struct.unpack_from(">q", data, offset)[0]
    return f64_from_raw(raw), offset + 8


def read_f32(data: bytes, offset: int) -> tuple[float, int]:
    raw = struct.unpack_from(">i", data, offset)[0]
    if raw >= 0x80000000:
        raw -= 1 << 32
    return raw / (1 << 16), offset + 4


def read_f64vec2(data: bytes, offset: int) -> tuple[dict[str, float], int]:
    x, offset = read_f64(data, offset)
    y, offset = read_f64(data, offset)
    return {"X": x, "Y": y}, offset


def read_f32vec2(data: bytes, offset: int) -> tuple[dict[str, float], int]:
    x, offset = read_f32(data, offset)
    y, offset = read_f32(data, offset)
    return {"X": x, "Y": y}, offset


def read_f32vec3(data: bytes, offset: int) -> tuple[dict[str, float], int]:
    x, offset = read_f32(data, offset)
    y, offset = read_f32(data, offset)
    z, offset = read_f32(data, offset)
    return {"X": x, "Y": y, "Z": z}, offset


def read_f64vec3(data: bytes, offset: int) -> tuple[dict[str, float], int]:
    x, offset = read_f64(data, offset)
    y, offset = read_f64(data, offset)
    z, offset = read_f64(data, offset)
    return {"X": x, "Y": y, "Z": z}, offset


def read_varint128(data: bytes, offset: int) -> tuple[int, int]:
    lo = struct.unpack_from(">q", data, offset)[0]
    hi = struct.unpack_from(">q", data, offset + 8)[0]
    raw = (hi << 64) | (lo & 0xFFFFFFFFFFFFFFFF)
    return raw, offset + 16
