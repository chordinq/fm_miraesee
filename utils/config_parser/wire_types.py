"""Metaplay tagged wire format primitives (from IOReader / TaggedWireSerializer)."""

from __future__ import annotations

import struct
from enum import IntEnum


class WireDataType(IntEnum):
    Invalid = 0
    Null = 1
    VarInt = 2
    VarInt128 = 3
    F32 = 4
    F32Vec2 = 5
    F32Vec3 = 6
    F64 = 7
    F64Vec2 = 8
    F64Vec3 = 9
    Float32 = 10
    Float64 = 11
    String = 12
    Bytes = 13
    AbstractStruct = 14
    NullableStruct = 15
    Struct = 16
    EndStruct = 17
    ValueCollection = 18
    KeyValueCollection = 19
    ObjectTable = 20


def read_varuint(data: bytes, offset: int) -> tuple[int, int]:
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


def read_varint(data: bytes, offset: int) -> tuple[int, int]:
    """IOReaderCursor.ReadVarInt: zigzag decode over varuint."""
    raw, offset = read_varuint(data, offset)
    value = -(raw & 1) ^ (raw >> 1)
    return value, offset


def read_varlong(data: bytes, offset: int) -> tuple[int, int]:
    """SkipWireType VarInt path uses ReadVarLong (same zigzag on varuint)."""
    return read_varint(data, offset)


def read_wire_type(data: bytes, offset: int) -> tuple[int, int]:
    if offset >= len(data):
        raise ValueError("unexpected end of data reading wire type")
    return data[offset], offset + 1


def read_tag_id(data: bytes, offset: int) -> tuple[int, int]:
    return read_varint(data, offset)
