"""Dump format contract shared by miraesee_data_exporter.lua and Python parser."""

from __future__ import annotations

DUMP_VERSION = 3

# [FORGE] meta line (32 hex chars, v3+):
#   forge_level(2) + forge_count(8, uint32) + forge_seed(16, uint64)
#   + highest_age(2, IL +0x40) + reserved(3) + asc(1)
# Summon meta lines (SKILL/MOUNT): level(2) + count(2) + seed(16) + pad(10) + asc(1)
# PET meta v4: level(2) + count(2) + seed(16) + hatch_slots(2) + pad(8) + asc(1)
SUMMON_META_LINE_LEN = 31
PET_META_LINE_LEN = 31

# Secondary stat blob: 10 chars per stat chunk (type nibble + 8 hex raw FD6-ish u32)
STATS_CHUNK_LEN = 10
COLLECTION_STATS_LEN = 20  # 2 chunks
EQUIPMENT_STATS_LEN = 20  # 2 chunks; line = header(12) + stats(20) = 32 hex chars
EQUIPMENT_LINE_LEN = 12 + EQUIPMENT_STATS_LEN

# Collection line lengths
COLLECTION_LINE_V1_LEN = 32
PET_MOUNT_LINE_V2_LEN = 44

# v1 pet/mount: header(4) + prog(8) + stats(20)
# v2 pet/mount: header(4) + prog(20) + stats(20)
#   prog v2 pet: level(8) + exp(8) + is_eq(2) + slot(2)
#   prog v2 mount: level(8) + exp(8) + is_eq(2) + pad(2)

EMPTY_EQUIP_SLOT = 0xFF

# Skin collection line:
#   prefix(1) + item_type(1) + idx(2) + is_eq(1) + level(2) + exp(8) + stats(20) = 35 chars
SKIN_LINE_LEN = 35
