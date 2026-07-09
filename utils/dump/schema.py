"""Dump format contract shared by utils/gg/miraesee_data_exporter.lua and Python parser."""

from __future__ import annotations

DUMP_VERSION = 4
LINE_WIDTH = 32

# Dump v4 — every `[BLOCK]` data line is exactly 32 hex chars (see utils/dump/wire.py).
#
# Multi-line records use continuation prefixes:
#   8 = secondary stats (20-char blob, previous 2/4/5 record)
#   9 = timer start ms (egg/forge/tech timer)
#   A = timer end ms
#   6 = skin guid lo / 7 = skin guid hi
#   E = equipped skin guid header (item_type + following 6/7 lines)
#
# Collection primary prefixes: 1=skill 2=pet 3=egg 4=mount 5=skin 5F=skin meta
#
# v4 primary line layouts (32 hex chars, zero-padded):
#   pet:  2 + rarity(1) + id(2) + level(8) + exp(8) + is_eq(2) + slot(2) + is_locked(2)
#   egg:  3 + rarity(1) + is_eq(2) + slot(2) + seed(16)
#   mount: 4 + rarity(1) + id(2) + level(8) + exp(8) + is_eq(2) + is_locked(2)
#   is_eq / slot / is_locked use full byte (%02X) so EMPTY_EQUIP_SLOT 0xFF encodes correctly.
CONT_STATS = "8"
CONT_TIMER_START = "9"
CONT_TIMER_END = "A"
CONT_GUID_LO = "6"
CONT_GUID_HI = "7"

# v4 record primary prefixes inside collection blocks
KIND_SKILL = "1"
KIND_PET = "2"
KIND_EGG = "3"
KIND_MOUNT = "4"
KIND_SKIN = "5"
SKIN_META_PREFIX = "5F"

# [FORGE] meta line (32 hex chars, v3+):#   forge_level(2) + forge_count(8, uint32) + forge_seed(16, uint64)
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
EGG_LINE_V2_LEN = 64
PET_MOUNT_LINE_V2_LEN = 44
PET_MOUNT_LINE_V2_LOCK_LEN = 46
FORGE_META_LINE_LEN = 32
FORGE_META_TIMER_SUFFIX_LEN = 32

# v1 pet/mount: header(4) + prog(8) + stats(20)
# v2 egg: header(4) + prog(28) + timer_start_ms(16) + timer_end_ms(16) = 64
#   prog: pad(4) + is_eq(2) + slot(2) + pad(4) + seed(16)
# FORGE meta timer suffix: start_ms(16) + end_ms(16) appended to 32-char forge line
# TECH_TREE_TIMERS line: tree_type(1) + node_id(2) + start_ms(16) + end_ms(16) = 35
TECH_TREE_TIMER_LINE_LEN = 35
#   prog v2 pet: level(8) + exp(8) + is_eq(2) + slot(2) [+ is_locked(2)]
#   prog v2 mount: level(8) + exp(8) + is_eq(2) + pad(2) [+ is_locked(2) at prog[20:22]]

EMPTY_EQUIP_SLOT = 0xFF

# Skin collection v1 line:
#   prefix(1) + item_type(1) + idx(2) + is_eq(1) + level(2) + exp(8) + stats(20) = 35 chars
SKIN_LINE_LEN = 35
# Skin collection v2 line: v1 + guid_lo(16) + guid_hi(16) = 67 chars
SKIN_LINE_V2_LEN = 67
# Skin collection meta line (35 chars): 5F + skins_random_seed(16) + pad(17)
SKIN_META_LINE_LEN = 35
