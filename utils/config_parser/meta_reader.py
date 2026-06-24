"""Decode Metaplay tagged serialization blobs (.mpc) into Python values."""

from __future__ import annotations

import struct
from typing import Any

from .f64 import read_f32, read_f32vec2, read_f32vec3, read_f64, read_f64vec2, read_f64vec3, read_varint128
from .wire_types import WireDataType, read_tag_id, read_varint, read_varlong, read_wire_type


def read_value_collection(data: bytes, offset: int) -> tuple[list[Any], int]:
    count, offset = read_varint(data, offset)
    if count < 0:
        return [], offset
    elem_wire, offset = read_wire_type(data, offset)
    items: list[Any] = []
    for _ in range(count):
        item, offset = read_wire_value(data, offset, elem_wire)
        items.append(item)
    return items, offset


def read_key_value_collection(data: bytes, offset: int) -> tuple[dict[Any, Any], int]:
    count, offset = read_varint(data, offset)
    if count < 0:
        return {}, offset
    key_wire, offset = read_wire_type(data, offset)
    val_wire, offset = read_wire_type(data, offset)
    out: dict[Any, Any] = {}
    for _ in range(count):
        key, offset = read_wire_value(data, offset, key_wire)
        val, offset = read_wire_value(data, offset, val_wire)
        out[key] = val
    return out, offset


def read_object_table_rows(data: bytes, offset: int) -> tuple[list[dict[int, Any]], int]:
    count, offset = read_varint(data, offset)
    if count < 0:
        return [], offset
    rows: list[dict[int, Any]] = []
    for _ in range(count):
        row, offset = read_struct_members(data, offset)
        rows.append(row)
    return rows, offset


def read_wire_value(data: bytes, offset: int, wire_type: int) -> tuple[Any, int]:
    if wire_type == 0:
        return None, offset

    if 21 <= wire_type <= 30:
        present, offset = read_varint(data, offset)
        if present == 0:
            return None, offset
        return read_wire_value(data, offset, wire_type - 19)

    wt = WireDataType(wire_type)

    if wt == WireDataType.Null:
        return None, offset
    if wt == WireDataType.VarInt:
        value, offset = read_varlong(data, offset)
        return value, offset
    if wt == WireDataType.VarInt128:
        value, offset = read_varint128(data, offset)
        return value, offset
    if wt == WireDataType.F32:
        return read_f32(data, offset)
    if wt == WireDataType.F32Vec2:
        return read_f32vec2(data, offset)
    if wt == WireDataType.F32Vec3:
        return read_f32vec3(data, offset)
    if wt == WireDataType.F64Vec2:
        return read_f64vec2(data, offset)
    if wt == WireDataType.F64Vec3:
        return read_f64vec3(data, offset)
    if wt == WireDataType.ValueCollection:
        return read_value_collection(data, offset)
    if wt == WireDataType.KeyValueCollection:
        return read_key_value_collection(data, offset)
    if wt == WireDataType.ObjectTable:
        return read_object_table_rows(data, offset)
    if wt == WireDataType.F64:
        return read_f64(data, offset)
    if wt == WireDataType.Float32:
        value = struct.unpack_from("<f", data, offset)[0]
        return value, offset + 4
    if wt == WireDataType.Float64:
        value = struct.unpack_from("<d", data, offset)[0]
        return value, offset + 8
    if wt == WireDataType.String:
        length, offset = read_varint(data, offset)
        if length < 0:
            return None, offset
        raw = data[offset : offset + length]
        return raw.decode("utf-8"), offset + length
    if wt == WireDataType.Bytes:
        length, offset = read_varint(data, offset)
        if length < 1:
            return b"", offset
        raw = data[offset : offset + length]
        return raw, offset + length
    if wt in (WireDataType.Struct,):
        return read_struct_members(data, offset)
    if wt == WireDataType.AbstractStruct:
        disc, offset = read_varint(data, offset)
        if disc == 0:
            return None, offset
        fields, offset = read_struct_members(data, offset)
        if isinstance(fields, dict):
            fields = dict(fields)
            fields["$type"] = disc
        return fields, offset
    if wt == WireDataType.NullableStruct:
        return read_nullable_struct(data, offset)

    raise ValueError(f"unsupported wire type for read: {wt.name} ({wire_type})")


def read_struct_members(data: bytes, offset: int) -> tuple[dict[int, Any], int]:
    """Tagged member stream terminated by EndStruct (DeserializeMembers pattern)."""
    fields: dict[int, Any] = {}
    while offset < len(data):
        wire_type, offset = read_wire_type(data, offset)
        if wire_type == WireDataType.EndStruct:
            break
        tag_id, offset = read_tag_id(data, offset)
        value, offset = read_wire_value(data, offset, wire_type)
        fields[tag_id] = value
    return fields, offset


def parse_object_table(data: bytes, offset: int = 0) -> tuple[list[dict[int, Any]], int]:
    """ObjectTable (wire 20): zigzag count + DeserializeMembers rows."""
    wire_type, offset = read_wire_type(data, offset)
    if wire_type != WireDataType.ObjectTable:
        raise ValueError(f"expected ObjectTable, got {wire_type}")
    rows, offset = read_object_table_rows(data, offset)
    return rows, offset


def read_nullable_struct(data: bytes, offset: int) -> tuple[dict[int, Any] | None, int]:
    if offset >= len(data):
        raise ValueError("missing nullable presence byte")
    if data[offset] == 0:
        return None, offset + 1
    return read_struct_members(data, offset + 1)


def parse_tagged_root(data: bytes) -> dict[int, Any]:
    """Parse a config .mpc blob (nullable class root)."""
    if not data:
        return {}

    wire_type, offset = read_wire_type(data, 0)
    if wire_type != WireDataType.NullableStruct:
        raise ValueError(f"expected NullableStruct root, got {wire_type}")

    fields, _ = read_nullable_struct(data, offset)
    return fields or {}


def map_fields(fields: dict[int, Any], schema: dict[int, str]) -> dict[str, Any]:
    return {name: fields[tag_id] for tag_id, name in schema.items() if tag_id in fields}
