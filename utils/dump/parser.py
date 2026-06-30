from __future__ import annotations

import re
from typing import Callable

from config import TECH_TREE_POSITION_LIBRARY
from core.game_logic.enums import TechTreeNodeType, TechTreeType

from .schema import (
	COLLECTION_LINE_V1_LEN,
	COLLECTION_STATS_LEN,
	DUMP_VERSION,
	EMPTY_EQUIP_SLOT,
	EQUIPMENT_STATS_LEN,
	FORGE_META_LINE_LEN,
	FORGE_META_TIMER_SUFFIX_LEN,
	PET_MOUNT_LINE_V2_LEN,
	PET_MOUNT_LINE_V2_LOCK_LEN,
	SKIN_LINE_LEN,
	TECH_TREE_TIMER_LINE_LEN,
)
from .snapshot import (
	DumpSnapshot,
	EggEntryDump,
	EquipmentItemDump,
	ForgeMetaDump,
	HiddenLevelDump,
	MountEntryDump,
	PetEntryDump,
	RoundRobinDump,
	SkinEntryDump,
	SkillEntryDump,
	SummonMetaDump,
	TechTreeNodeDump,
	TechTreeTimerDump,
)

BLOCK_HEADER = re.compile(r"^\[([A-Z_]+)\]$")
SUMMON_META = re.compile(r"^([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{16})")
PET_META_V4 = re.compile(
	r"^([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{16})"
	r"([0-9A-Fa-f]{2})00000000([0-9A-Fa-f])$"
)
FORGE_META_V3 = re.compile(
	r"^([0-9A-Fa-f]{2})([0-9A-Fa-f]{8})([0-9A-Fa-f]{16})"
	r"([0-9A-Fa-f]{2})000([0-9A-Fa-f])$"
)
CURRENCY_LINE = re.compile(r"^[0-9A-Fa-f]{32}$")
SKILL_COLL_LINE = re.compile(
	r"^1([0-9A-Fa-f]{2})0([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})[0-9A-Fa-f]{20}$"
)
COLLECTION_HEADER = re.compile(r"^([0-9A-Fa-f])([0-9A-Fa-f])([0-9A-Fa-f]{2})")
# 5 <type:1> <idx:2> <is_eq:1> <level:2> <exp:8> <stats:20>
SKIN_LINE = re.compile(
	r"^5([0-9A-Fa-f])([0-9A-Fa-f]{2})([0-9A-Fa-f])([0-9A-Fa-f]{2})([0-9A-Fa-f]{8})"
	r"([0-9A-Fa-f]{20})$"
)


def _build_techtree_lookup() -> dict[tuple[int, int], tuple[TechTreeNodeType, int]]:
	lookup: dict[tuple[int, int], tuple[TechTreeNodeType, int]] = {}
	name_to_int = {t.name: t.value for t in TechTreeType}
	for tree_name, tree_data in TECH_TREE_POSITION_LIBRARY.items():
		t_type_int = name_to_int.get(tree_name)
		if t_type_int is None:
			continue
		occurrence: dict[str, int] = {}
		for node in sorted(tree_data["Nodes"], key=lambda n: n["Id"]):
			local_id = node["Id"]
			type_name = node["Type"]
			try:
				node_type = TechTreeNodeType[type_name]
			except KeyError:
				continue
			tier = occurrence.get(type_name, 0)
			occurrence[type_name] = tier + 1
			lookup[(t_type_int, local_id)] = (node_type, tier)
	return lookup


_TECHTREE_LOOKUP = _build_techtree_lookup()


def parse_dump_text(text: str) -> DumpSnapshot:
	return DumpTextParser().parse(text)


class DumpTextParser:
	def __init__(self) -> None:
		self._handlers: dict[str, Callable[[DumpSnapshot, list[str]], None]] = {
			"DUMP_VERSION": self._parse_version,
			"CURRENCY": self._parse_currency,
			"TECH_TREE": self._parse_techtree,
			"TECH_TREE_TIMERS": self._parse_techtree_timers,
			"FORGE": self._parse_forge_meta,
			"SKILL": self._parse_skill_meta,
			"PET": self._parse_pet_meta,
			"MOUNT": self._parse_mount_meta,
			"SKILL_COLLECTION": self._parse_skill_collection,
			"PET_EGG_COLLECTION": self._parse_pet_egg_collection,
			"MOUNT_COLLECTION": self._parse_mount_collection,
			"HIDDEN_LEVELS": self._parse_hidden_levels,
			"ITEM_ROUND_ROBIN": self._parse_round_robin,
			"EQUIPMENT": self._parse_equipment,
			"SKIN_COLLECTION": self._parse_skin_collection,
		}

	def parse(self, text: str) -> DumpSnapshot:
		snapshot = DumpSnapshot()
		for block_name, lines in self._split_blocks(text).items():
			handler = self._handlers.get(block_name)
			if handler:
				handler(snapshot, lines)
		return snapshot

	def _split_blocks(self, text: str) -> dict[str, list[str]]:
		blocks: dict[str, list[str]] = {}
		current_name: str | None = None
		current_lines: list[str] = []

		for raw_line in text.splitlines():
			line = raw_line.strip()
			if not line:
				if current_name is not None:
					blocks[current_name] = current_lines
					current_name = None
					current_lines = []
				continue

			header = BLOCK_HEADER.match(line)
			if header:
				if current_name is not None:
					blocks[current_name] = current_lines
				current_name = header.group(1)
				current_lines = []
				continue

			if current_name is not None:
				current_lines.append(line)

		if current_name is not None:
			blocks[current_name] = current_lines
		return blocks

	def _parse_version(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if lines:
			try:
				snapshot.version = int(lines[0])
			except ValueError:
				snapshot.version = DUMP_VERSION

	def _parse_meta_line(self, line: str) -> tuple[int, int, int, int] | None:
		m = SUMMON_META.match(line)
		if not m:
			return None
		byte1 = int(m.group(1), 16)
		byte2 = int(m.group(2), 16)
		seed = int(m.group(3), 16)
		asc = int(line[-1], 16) if len(line) > 20 else 0
		return byte1, byte2, seed, asc

	def _parse_timer_suffix(self, line: str, base_len: int) -> tuple[int, int]:
		if len(line) < base_len + FORGE_META_TIMER_SUFFIX_LEN:
			return 0, 0
		offset = base_len
		return (
			int(line[offset : offset + 16], 16),
			int(line[offset + 16 : offset + 32], 16),
		)

	def _parse_forge_meta_line(
		self, line: str, version: int
	) -> tuple[int, int, int, int, int] | None:
		match = FORGE_META_V3.match(line)
		if match:
			return (
				int(match.group(1), 16),
				int(match.group(2), 16),
				int(match.group(3), 16),
				int(match.group(4), 16),
				int(match.group(5), 16),
			)
		# v2 fallback: forge_count was incorrectly truncated to 1 byte (summon wire).
		raw = self._parse_meta_line(line)
		if raw is None:
			return None
		level, count_byte, seed, asc = raw
		return level, count_byte, seed, 0, asc

	def _parse_forge_meta(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if not lines:
			return
		raw = self._parse_forge_meta_line(lines[0], snapshot.version)
		if not raw:
			return
		level, count, seed, highest_age, asc = raw
		timer_start_ms, timer_end_ms = self._parse_timer_suffix(lines[0], FORGE_META_LINE_LEN)
		snapshot.forge_meta = ForgeMetaDump(
			forge_level=level,
			forge_count=count,
			forge_seed=seed,
			highest_age_of_crafted_item=highest_age,
			ascension_level=asc,
			timer_start_ms=timer_start_ms,
			timer_end_ms=timer_end_ms,
		)

	def _apply_summon_meta(self, target: SummonMetaDump, line: str) -> None:
		raw = self._parse_meta_line(line)
		if not raw:
			return
		# Lua extract_summon_meta: format(level, count, seed) — byte1=level, byte2=count
		level, count, seed, asc = raw
		target.level = level
		target.count = count
		target.seed = seed
		target.ascension_level = asc

	def _parse_skill_meta(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if lines:
			meta = SummonMetaDump()
			self._apply_summon_meta(meta, lines[0])
			snapshot.skill_summon_meta = meta

	def _parse_pet_meta_line(self, line: str) -> tuple[int, int, int, int, int] | None:
		match = PET_META_V4.match(line)
		if match:
			return (
				int(match.group(1), 16),
				int(match.group(2), 16),
				int(match.group(3), 16),
				int(match.group(4), 16),
				int(match.group(5), 16),
			)
		raw = self._parse_meta_line(line)
		if raw is None:
			return None
		level, count, seed, asc = raw
		return level, count, seed, 0, asc

	def _parse_pet_meta(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if not lines:
			return
		raw = self._parse_pet_meta_line(lines[0])
		if not raw:
			return
		level, count, seed, hatch_slots, asc = raw
		snapshot.pet_summon_meta = SummonMetaDump(
			level=level,
			count=count,
			seed=seed,
			ascension_level=asc,
			hatch_slots_count=hatch_slots,
		)

	def _parse_mount_meta(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if lines:
			meta = SummonMetaDump()
			self._apply_summon_meta(meta, lines[0])
			snapshot.mount_summon_meta = meta

	def _parse_currency(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		# Lua extract_currency: 4 amounts per line, sequential dict entry order.
		base_idx = 0
		for line in lines:
			if not CURRENCY_LINE.match(line):
				continue
			for i in range(0, 32, 8):
				snapshot.currencies[base_idx + i // 8] = int(line[i : i + 8], 16)
			base_idx += 4

	def _parse_techtree(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk[0] in "Ff":
					continue
				try:
					t_type_val = int(chunk[0], 16)
					local_id = int(chunk[1:3], 16)
					level = int(chunk[3], 16)
					if _TECHTREE_LOOKUP.get((t_type_val, local_id)) is None:
						continue
					snapshot.techtree_nodes.append(
						TechTreeNodeDump(
							tree_type=t_type_val,
							local_id=local_id,
							ui_level=level + 1,
						)
					)
				except ValueError:
					continue

	def _parse_techtree_timers(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			if len(line) < TECH_TREE_TIMER_LINE_LEN:
				continue
			try:
				tree_type = int(line[0], 16)
				local_id = int(line[1:3], 16)
				timer_start_ms = int(line[3:19], 16)
				timer_end_ms = int(line[19:35], 16)
			except ValueError:
				continue
			if timer_end_ms <= timer_start_ms:
				continue
			snapshot.techtree_timers.append(
				TechTreeTimerDump(
					tree_type=tree_type,
					local_id=local_id,
					timer_start_ms=timer_start_ms,
					timer_end_ms=timer_end_ms,
				)
			)

	def _parse_skill_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			m = SKILL_COLL_LINE.match(line)
			if not m:
				continue
			snapshot.skills.append(
				SkillEntryDump(
					combat_skill_enum=int(m.group(1), 16),
					level=int(m.group(2), 16),
					shard_count=int(m.group(3), 16),
					is_equipped=int(m.group(4), 16) != 0,
					equip_slot=int(m.group(5), 16),
				)
			)

	def _parse_pet_v1(self, rarity: int, pet_id: int, prog: str, stats: str) -> PetEntryDump:
		return PetEntryDump(
			rarity=rarity,
			pet_id=pet_id,
			level=int(prog[0:2], 16),
			experience=int(prog[2:4], 16),
			is_equipped=int(prog[4:6], 16) != 0,
			equip_slot=int(prog[6:8], 16),
			is_locked=False,
			stats_blob=stats,
		)

	def _parse_pet_v2(
		self,
		rarity: int,
		pet_id: int,
		prog: str,
		stats: str,
		*,
		is_locked: bool = False,
	) -> PetEntryDump:
		return PetEntryDump(
			rarity=rarity,
			pet_id=pet_id,
			level=int(prog[0:8], 16),
			experience=int(prog[8:16], 16),
			is_equipped=int(prog[16:18], 16) != 0,
			equip_slot=int(prog[18:20], 16),
			is_locked=is_locked,
			stats_blob=stats,
		)

	def _parse_egg(self, rarity: int, prog: str, line: str) -> EggEntryDump:
		timer_start_ms, timer_end_ms = self._parse_timer_suffix(line, COLLECTION_LINE_V1_LEN)
		return EggEntryDump(
			rarity=rarity,
			is_equipped=int(prog[4:6], 16) != 0,
			equip_slot=int(prog[6:8], 16),
			seed=int(prog[12:28], 16),
			timer_start_ms=timer_start_ms,
			timer_end_ms=timer_end_ms,
		)

	def _parse_mount_v1(self, rarity: int, mount_id: int, prog: str, stats: str) -> MountEntryDump:
		return MountEntryDump(
			rarity=rarity,
			mount_id=mount_id,
			level=int(prog[0:2], 16),
			experience=int(prog[2:4], 16),
			is_equipped=int(prog[4:6], 16) != 0,
			is_locked=False,
			stats_blob=stats,
		)

	def _parse_mount_v2(
		self,
		rarity: int,
		mount_id: int,
		prog: str,
		stats: str,
		*,
		is_locked: bool = False,
	) -> MountEntryDump:
		return MountEntryDump(
			rarity=rarity,
			mount_id=mount_id,
			level=int(prog[0:8], 16),
			experience=int(prog[8:16], 16),
			is_equipped=int(prog[16:18], 16) != 0,
			is_locked=is_locked,
			stats_blob=stats,
		)

	def _parse_pet_egg_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			header = COLLECTION_HEADER.match(line)
			if not header:
				continue
			kind = header.group(1)
			rarity = int(header.group(2), 16)
			entry_id = int(header.group(3), 16)

			if kind == "2":
				if len(line) >= PET_MOUNT_LINE_V2_LOCK_LEN:
					prog = line[4:26]
					stats = line[26:46]
					is_locked = int(prog[20:22], 16) != 0
					snapshot.pets.append(
						self._parse_pet_v2(
							rarity,
							entry_id,
							prog,
							stats,
							is_locked=is_locked,
						)
					)
				elif len(line) == PET_MOUNT_LINE_V2_LEN:
					prog = line[4:24]
					stats = line[24:44]
					snapshot.pets.append(self._parse_pet_v2(rarity, entry_id, prog, stats))
				elif len(line) >= COLLECTION_LINE_V1_LEN:
					prog = line[4:12]
					stats = line[12:32]
					snapshot.pets.append(self._parse_pet_v1(rarity, entry_id, prog, stats))
			elif kind == "3" and len(line) >= COLLECTION_LINE_V1_LEN:
				prog = line[4:32]
				snapshot.eggs.append(self._parse_egg(rarity, prog, line))

	def _parse_mount_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			header = COLLECTION_HEADER.match(line)
			if not header or header.group(1) != "4":
				continue
			rarity = int(header.group(2), 16)
			mount_id = int(header.group(3), 16)
			if len(line) >= PET_MOUNT_LINE_V2_LOCK_LEN:
				prog = line[4:26]
				stats = line[26:46]
				is_locked = int(prog[20:22], 16) != 0
				snapshot.mounts.append(
					self._parse_mount_v2(
						rarity,
						mount_id,
						prog,
						stats,
						is_locked=is_locked,
					)
				)
			elif len(line) == PET_MOUNT_LINE_V2_LEN:
				prog = line[4:24]
				stats = line[24:44]
				snapshot.mounts.append(self._parse_mount_v2(rarity, mount_id, prog, stats))
			elif len(line) >= COLLECTION_LINE_V1_LEN:
				prog = line[4:12]
				stats = line[12:32]
				snapshot.mounts.append(self._parse_mount_v1(rarity, mount_id, prog, stats))

	def _parse_hidden_levels(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		# Wire: type(1 hex) + age(1 hex) + bracket_key(2 hex)
		# bracket_key indexes ItemLevelBracketsLibrary (e.g. 18 → Lv 90~98)
		merged: dict[tuple[int, int], int] = {}
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk[0] in "Ff" or chunk.upper() == "F000":
					continue
				try:
					item_type = int(chunk[0], 16)
					age = int(chunk[1], 16)
					level = int(chunk[2:4], 16)
				except ValueError:
					continue
				if item_type > 7 or age > 9 or level > 99:
					continue
				key = (item_type, age)
				if key not in merged or level > merged[key]:
					merged[key] = level
		for (item_type, age), level in sorted(merged.items()):
			snapshot.hidden_levels.append(
				HiddenLevelDump(item_type=item_type, age=age, level=level)
			)

	def _parse_round_robin(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk == "0000":
					continue
				try:
					bitmask = int(chunk[2:4], 16)
					snapshot.round_robins.append(
						RoundRobinDump(
							item_type=int(chunk[0], 16),
							age=int(chunk[1], 16),
							indices=[i for i in range(8) if bitmask & (1 << i)],
						)
					)
				except ValueError:
					continue

	def _parse_equipment(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in lines:
			if len(line) < 12 or line.startswith("00000000"):
				continue
			stats_blob = line[12 : 12 + EQUIPMENT_STATS_LEN]
			snapshot.equipment_slots.append(
				EquipmentItemDump(
					age=int(line[1], 16),
					item_type=int(line[2], 16),
					idx=int(line[3], 16),
					level=int(line[4:6], 16),
					stats_blob=stats_blob,
				)
			)

	def _parse_skin_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		"""Parse [SKIN_COLLECTION] block.

		Each skin line (35 chars):
		    5 <item_type:1hex> <idx:02hex> <is_eq:1hex> <level:02hex> <exp:08hex> <stats:20hex>
		"""
		for line in lines:
			if len(line) != SKIN_LINE_LEN:
				continue
			m = SKIN_LINE.match(line)
			if not m:
				continue
			snapshot.skins.append(
				SkinEntryDump(
					item_type=int(m.group(1), 16),
					idx=int(m.group(2), 16),
					is_equipped=int(m.group(3), 16) != 0,
					level=int(m.group(4), 16),
					experience=int(m.group(5), 16),
					stats_blob=m.group(6),
				)
			)
