"""Trace full RandomValueStatContribution wire bytes."""

from __future__ import annotations

from pathlib import Path

from utils.config_parser import meta_reader
from utils.config_parser.wire_types import WireDataType, read_varint, read_wire_type


def read_struct_members_traced(data: bytes, offset: int, label: str) -> tuple[dict, int]:
    fields: dict = {}
    print(f"\n=== {label} @ {offset} ===")
    start = offset
    while offset < len(data):
        wt_off = offset
        wire_type, offset = read_wire_type(data, offset)
        wt_name = WireDataType(wire_type).name if wire_type in WireDataType._value2member_map_ else "?"
        print(f"  @{wt_off}: wire={wire_type} ({wt_name})")
        if wire_type == WireDataType.EndStruct:
            print("  EndStruct")
            break
        tag_id, offset = read_varint(data, offset)
        val_off = offset
        value, offset = meta_reader.read_wire_value(data, offset, wire_type)
        print(f"  tag={tag_id} value={value!r} payload={data[val_off:offset].hex()}")
        fields[tag_id] = value
    print(f"  total={offset - start} bytes")
    return fields, offset


def skip_one_member(data: bytes, offset: int) -> int:
    wire_type, offset = read_wire_type(data, offset)
    if wire_type == WireDataType.EndStruct:
        return offset
    _, offset = read_varint(data, offset)
    _, offset = meta_reader.read_wire_value(data, offset, wire_type)
    return offset


blob = Path("core_test/_sgc_26_6_30/mpc/SkinsLibrary.mpc").read_bytes()
off = 0
_, off = read_wire_type(blob, off)
_, off = read_varint(blob, off)
off = skip_one_member(blob, off)  # SkinId
wt, off = read_wire_type(blob, off)
count, off = read_varint(blob, off)
elem_wt, off = read_wire_type(blob, off)
print(f"PossibleStats count={count} elem_wt={elem_wt} ({WireDataType(elem_wt).name})")
_, off = read_struct_members_traced(blob, off, "RandomValueStatContribution[0]")
