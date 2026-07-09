"""Dump format v4 — all block data lines are 32 hex chars."""

from __future__ import annotations

import re

from .schema import EMPTY_EQUIP_SLOT
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
from .wire import (
	CONT_GUID_HI,
	CONT_GUID_LO,
	CONT_STATS,
	CONT_TIMER_END,
	CONT_TIMER_START,
	KIND_EGG,
	KIND_EQUIPPED,
	KIND_MOUNT,
	KIND_PET,
	KIND_SKILL,
	KIND_SKIN,
	LINE_WIDTH,
	SKIN_META_PREFIX,
	is_v4_line,
	parse_pet_meta_line,
	parse_skin_meta_seed,
	parse_stats_line,
	parse_summon_meta_line,
	parse_timer_end_line,
	parse_timer_start_line,
)

FORGE_META_V4 = re.compile(
	r"^([0-9A-Fa-f]{2})([0-9A-Fa-f]{8})([0-9A-Fa-f]{16})"
	r"([0-9A-Fa-f]{2})000([0-9A-Fa-f])$"
)
SKILL_V4 = re.compile(
	r"^1([0-9A-Fa-f]{2})0([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})"
)


class _PendingRecord:
	__slots__ = ("kind", "fields")

	def __init__(self, kind: str, fields: dict) -> None:
		self.kind = kind
		self.fields = fields


class DumpV4Parser:
	def parse_block(self, block_name: str, lines: list[str], snapshot: DumpSnapshot) -> None:
		handler = getattr(self, f"_parse_{block_name.lower()}", None)
		if handler is None:
			return
		handler(snapshot, lines)

	def _lines(self, lines: list[str]) -> list[str]:
		return [line.strip().upper() for line in lines if line.strip()]

	def _parse_dump_version(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		if lines:
			try:
				snapshot.version = int(lines[0])
			except ValueError:
				pass

	def _parse_currency(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		base_idx = 0
		for line in self._lines(lines):
			if len(line) != LINE_WIDTH:
				continue
			for index in range(0, LINE_WIDTH, 8):
				snapshot.currencies[base_idx + index // 8] = int(line[index : index + 8], 16)
			base_idx += 4

	def _parse_forge(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		rows = self._lines(lines)
		if not rows:
			return
		match = FORGE_META_V4.match(rows[0])
		if not match:
			return
		timer_start_ms = 0
		timer_end_ms = 0
		if len(rows) > 1 and rows[1].startswith(CONT_TIMER_START):
			timer_start_ms = parse_timer_start_line(rows[1]) or 0
			if len(rows) > 2 and rows[2].startswith(CONT_TIMER_END):
				timer_end_ms = parse_timer_end_line(rows[2]) or 0
		snapshot.forge_meta = ForgeMetaDump(
			forge_level=int(match.group(1), 16),
			forge_count=int(match.group(2), 16),
			forge_seed=int(match.group(3), 16),
			highest_age_of_crafted_item=int(match.group(4), 16),
			ascension_level=int(match.group(5), 16),
			timer_start_ms=timer_start_ms,
			timer_end_ms=timer_end_ms,
		)

	def _apply_summon_meta(self, target: SummonMetaDump, line: str) -> None:
		raw = parse_summon_meta_line(line)
		if raw is None:
			return
		level, count, seed, asc = raw
		target.level = level
		target.count = count
		target.seed = seed
		target.ascension_level = asc

	def _parse_skill(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		rows = self._lines(lines)
		if not rows:
			return
		meta = SummonMetaDump()
		self._apply_summon_meta(meta, rows[0])
		snapshot.skill_summon_meta = meta

	def _parse_pet(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		rows = self._lines(lines)
		if not rows:
			return
		raw = parse_pet_meta_line(rows[0])
		if raw is None:
			return
		level, count, seed, hatch_slots, asc = raw
		snapshot.pet_summon_meta = SummonMetaDump(
			level=level,
			count=count,
			seed=seed,
			hatch_slots_count=hatch_slots,
			ascension_level=asc,
		)

	def _parse_mount(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		rows = self._lines(lines)
		if not rows:
			return
		meta = SummonMetaDump()
		self._apply_summon_meta(meta, rows[0])
		snapshot.mount_summon_meta = meta

	def _parse_skill_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in self._lines(lines):
			match = SKILL_V4.match(line)
			if not match:
				continue
			snapshot.skills.append(
				SkillEntryDump(
					combat_skill_enum=int(match.group(1), 16),
					level=int(match.group(2), 16),
					shard_count=int(match.group(3), 16),
					is_equipped=int(match.group(4), 16) != 0,
					equip_slot=int(match.group(5), 16),
				)
			)

	def _parse_pet_egg_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		pending: _PendingRecord | None = None
		for line in self._lines(lines):
			if not is_v4_line(line):
				continue
			if line.startswith(SKIN_META_PREFIX):
				continue

			if line[0] == KIND_PET:
				if pending is not None:
					self._flush_pending(snapshot, pending)
				pending = _PendingRecord(
					KIND_PET,
					{
						"rarity": int(line[1], 16),
						"pet_id": int(line[2:4], 16),
						"level": int(line[4:12], 16),
						"experience": int(line[12:20], 16),
						"is_equipped": int(line[20:22], 16) != 0,
						"equip_slot": int(line[22:24], 16),
						"is_locked": int(line[24:26], 16) != 0,
						"stats_blob": "00000000000000000000",
					},
				)
				continue

			if line[0] == KIND_EGG:
				if pending is not None:
					self._flush_pending(snapshot, pending)
				pending = _PendingRecord(
					KIND_EGG,
					{
						"rarity": int(line[1], 16),
						"is_equipped": int(line[2:4], 16) != 0,
						"equip_slot": int(line[4:6], 16),
						"seed": int(line[6:22], 16),
						"timer_start_ms": 0,
						"timer_end_ms": 0,
					},
				)
				continue

			if pending is None:
				continue

			if line.startswith(CONT_STATS):
				stats = parse_stats_line(line)
				if stats is not None:
					pending.fields["stats_blob"] = stats
				if pending.kind == KIND_PET:
					self._flush_pending(snapshot, pending)
					pending = None
				continue

			if pending.kind == KIND_EGG and line.startswith(CONT_TIMER_START):
				pending.fields["timer_start_ms"] = parse_timer_start_line(line) or 0
				continue

			if pending.kind == KIND_EGG and line.startswith(CONT_TIMER_END):
				pending.fields["timer_end_ms"] = parse_timer_end_line(line) or 0
				self._flush_pending(snapshot, pending)
				pending = None
				continue

		if pending is not None:
			self._flush_pending(snapshot, pending)

	def _flush_pending(self, snapshot: DumpSnapshot, pending: _PendingRecord) -> None:
		if pending.kind == KIND_PET:
			fields = pending.fields
			snapshot.pets.append(
				PetEntryDump(
					rarity=fields["rarity"],
					pet_id=fields["pet_id"],
					level=fields["level"],
					experience=fields["experience"],
					is_equipped=fields["is_equipped"],
					equip_slot=fields["equip_slot"],
					is_locked=fields["is_locked"],
					stats_blob=fields["stats_blob"],
				)
			)
			return
		if pending.kind == KIND_EGG:
			fields = pending.fields
			snapshot.eggs.append(
				EggEntryDump(
					rarity=fields["rarity"],
					is_equipped=fields["is_equipped"],
					equip_slot=fields["equip_slot"],
					seed=fields["seed"],
					timer_start_ms=fields["timer_start_ms"],
					timer_end_ms=fields["timer_end_ms"],
				)
			)

	def _parse_mount_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		pending: _PendingRecord | None = None
		for line in self._lines(lines):
			if not is_v4_line(line):
				continue

			if line[0] == KIND_MOUNT:
				if pending is not None:
					self._flush_mount(snapshot, pending)
				pending = _PendingRecord(
					KIND_MOUNT,
					{
						"rarity": int(line[1], 16),
						"mount_id": int(line[2:4], 16),
						"level": int(line[4:12], 16),
						"experience": int(line[12:20], 16),
						"is_equipped": int(line[20:22], 16) != 0,
						"is_locked": int(line[22:24], 16) != 0,
						"stats_blob": "00000000000000000000",
					},
				)
				continue

			if pending is None:
				continue

			if line.startswith(CONT_STATS):
				stats = parse_stats_line(line)
				if stats is not None:
					pending.fields["stats_blob"] = stats
				self._flush_mount(snapshot, pending)
				pending = None

		if pending is not None:
			self._flush_mount(snapshot, pending)

	def _flush_mount(self, snapshot: DumpSnapshot, pending: _PendingRecord) -> None:
		fields = pending.fields
		snapshot.mounts.append(
			MountEntryDump(
				rarity=fields["rarity"],
				mount_id=fields["mount_id"],
				level=fields["level"],
				experience=fields["experience"],
				is_equipped=fields["is_equipped"],
				is_locked=fields["is_locked"],
				stats_blob=fields["stats_blob"],
			)
		)

	def _parse_skin_collection(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		pending: _PendingRecord | None = None
		for line in self._lines(lines):
			if not is_v4_line(line):
				continue
			if line.startswith(SKIN_META_PREFIX):
				meta_seed = parse_skin_meta_seed(line)
				if meta_seed is not None:
					snapshot.skins_random_seed = meta_seed
				continue

			if line.startswith("5E"):
				continue

			if line[0] == KIND_EQUIPPED:
				continue

			if line[0] == KIND_SKIN:
				if pending is not None:
					self._flush_skin(snapshot, pending)
				pending = _PendingRecord(
					KIND_SKIN,
					{
						"item_type": int(line[1], 16),
						"idx": int(line[2:4], 16),
						"is_equipped": int(line[4], 16) != 0,
						"level": int(line[5:7], 16),
						"experience": int(line[7:15], 16),
						"stats_blob": "00000000000000000000",
					},
				)
				continue

			if pending is None:
				continue

			if line.startswith(CONT_STATS):
				stats = parse_stats_line(line)
				if stats is not None:
					pending.fields["stats_blob"] = stats
				self._flush_skin(snapshot, pending)
				pending = None
				continue

			if line.startswith(CONT_GUID_LO) or line.startswith(CONT_GUID_HI):
				continue

		if pending is not None:
			self._flush_skin(snapshot, pending)

	def _flush_skin(self, snapshot: DumpSnapshot, pending: _PendingRecord) -> None:
		fields = pending.fields
		snapshot.skins.append(
			SkinEntryDump(
				item_type=fields["item_type"],
				idx=fields["idx"],
				is_equipped=fields["is_equipped"],
				level=fields["level"],
				experience=fields["experience"],
				stats_blob=fields["stats_blob"],
			)
		)

	def _parse_equipment(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in self._lines(lines):
			if len(line) != LINE_WIDTH or line.startswith("00000000"):
				continue
			snapshot.equipment_slots.append(
				EquipmentItemDump(
					age=int(line[1], 16),
					item_type=int(line[2], 16),
					idx=int(line[3], 16),
					level=int(line[4:6], 16),
					stats_blob=line[12:32],
				)
			)

	def _parse_tech_tree(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		from .parser import _TECHTREE_LOOKUP

		for line in self._lines(lines):
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk[0] in "Ff":
					continue
				try:
					t_type_val = int(chunk[0], 16)
					local_id = int(chunk[1:3], 16)
					level_nibble = int(chunk[3], 16)
					if _TECHTREE_LOOKUP.get((t_type_val, local_id)) is None:
						continue
					internal_level = -1 if level_nibble == 0xF else level_nibble
					snapshot.techtree_nodes.append(
						TechTreeNodeDump(
							tree_type=t_type_val,
							local_id=local_id,
							ui_level=internal_level + 1,
						)
					)
				except ValueError:
					continue

	def _parse_tech_tree_timers(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		rows = self._lines(lines)
		index = 0
		while index < len(rows):
			line = rows[index]
			if len(line) != LINE_WIDTH:
				index += 1
				continue
			try:
				tree_type = int(line[0], 16)
				local_id = int(line[1:3], 16)
				timer_start_ms = int(line[3:19], 16)
			except ValueError:
				index += 1
				continue
			timer_end_ms = 0
			if index + 1 < len(rows) and rows[index + 1].startswith(CONT_TIMER_END):
				timer_end_ms = parse_timer_end_line(rows[index + 1]) or 0
				index += 1
			if timer_end_ms > timer_start_ms:
				snapshot.techtree_timers.append(
					TechTreeTimerDump(
						tree_type=tree_type,
						local_id=local_id,
						timer_start_ms=timer_start_ms,
						timer_end_ms=timer_end_ms,
					)
				)
			index += 1

	def _parse_hidden_levels(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		merged: dict[tuple[int, int], int] = {}
		for line in self._lines(lines):
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

	def _parse_item_round_robin(self, snapshot: DumpSnapshot, lines: list[str]) -> None:
		for line in self._lines(lines):
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
