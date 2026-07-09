"""Dump v4 wire helpers — every data line is exactly 32 hex chars."""

from __future__ import annotations

LINE_WIDTH = 32

KIND_SKILL = "1"
KIND_PET = "2"
KIND_EGG = "3"
KIND_MOUNT = "4"
KIND_SKIN = "5"
SKIN_META_PREFIX = "5F"

CONT_STATS = "8"
CONT_TIMER_START = "9"
CONT_TIMER_END = "A"
CONT_GUID_LO = "6"
CONT_GUID_HI = "7"
KIND_EQUIPPED = "E"


def pad32(payload: str) -> str:
	text = payload.upper()
	if len(text) > LINE_WIDTH:
		return text[:LINE_WIDTH]
	return text + ("0" * (LINE_WIDTH - len(text)))


def is_v4_line(line: str) -> bool:
	return len(line) == LINE_WIDTH and all(ch in "0123456789ABCDEFabcdef" for ch in line)


def pack_fragments(*fragments: str) -> list[str]:
	"""Pack hex fragments into 32-char lines (for dense blocks like TECH_TREE)."""
	blob = "".join(fragments).upper()
	lines: list[str] = []
	for index in range(0, len(blob), LINE_WIDTH):
		lines.append(pad32(blob[index : index + LINE_WIDTH]))
	return lines


def split_timer_suffix(start_ms: int, end_ms: int) -> tuple[str, str]:
	return (
		pad32(f"{CONT_TIMER_START}{start_ms:016X}"),
		pad32(f"{CONT_TIMER_END}{end_ms:016X}"),
	)


def parse_timer_start_line(line: str) -> int | None:
	if not line.startswith(CONT_TIMER_START):
		return None
	return int(line[1:17], 16)


def parse_timer_end_line(line: str) -> int | None:
	if not line.startswith(CONT_TIMER_END):
		return None
	return int(line[1:17], 16)


def parse_stats_line(line: str) -> str | None:
	if not line.startswith(CONT_STATS):
		return None
	return line[1:21]


def parse_guid_lo_line(line: str) -> int | None:
	if not line.startswith(CONT_GUID_LO):
		return None
	return int(line[1:17], 16)


def parse_guid_hi_line(line: str) -> int | None:
	if not line.startswith(CONT_GUID_HI):
		return None
	return int(line[1:17], 16)


SUMMON_META_WIDTH = 31
PET_META_WIDTH = 31


def normalize_meta_payload(line: str, width: int) -> str | None:
	text = line.strip().upper()
	if len(text) < width:
		return None
	return text[:width]


def parse_summon_meta_line(line: str) -> tuple[int, int, int, int] | None:
	"""Summon meta: level, count, seed, ascension."""
	payload = normalize_meta_payload(line, SUMMON_META_WIDTH)
	if payload is None:
		return None
	return (
		int(payload[0:2], 16),
		int(payload[2:4], 16),
		int(payload[4:20], 16),
		int(payload[30], 16),
	)


def parse_pet_meta_line(line: str) -> tuple[int, int, int, int, int] | None:
	"""Pet summon meta: level, count, seed, hatch_slots, ascension."""
	payload = normalize_meta_payload(line, PET_META_WIDTH)
	if payload is None:
		return None
	return (
		int(payload[0:2], 16),
		int(payload[2:4], 16),
		int(payload[4:20], 16),
		int(payload[20:22], 16),
		int(payload[30], 16),
	)


def parse_skin_meta_seed(line: str) -> int | None:
	text = line.strip().upper()
	if not text.startswith(SKIN_META_PREFIX) or len(text) < 18:
		return None
	return int(text[2:18], 16)
