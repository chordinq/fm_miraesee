# utils/parser.py
"""
Parse GameGuardian / miraesee_data_exporter.lua text dumps into PlayerModel.

Blocks are separated by blank lines. Each block starts with a [TAG] header line.
"""

from __future__ import annotations

import re
from typing import Callable

from configs import SKILL_MAPPING, TECH_TREE_POSITION_LIBRARY
from core.enums import CurrencyType, ItemAge, ItemType, Rarity, SecondaryStatType, TechTreeNodeType, TechTreeType
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.player_model.StatModel import StatModel

_U32_DENOM = 4294967296
_STATS_CHUNK_LEN = 10
_MAX_COLLECTION_STATS = 2
_MAX_EQUIPMENT_STATS = 4
_EQUIPMENT_STATS_BLOB_LEN = _STATS_CHUNK_LEN * _MAX_EQUIPMENT_STATS


def _build_techtree_lookup() -> dict[tuple[int, int], tuple[TechTreeNodeType, int]]:
	"""
	Build a lookup from (TechTreeType int, local_id) ? (TechTreeNodeType, tier_index).

	TechTreePositionLibrary maps tree names to ordered node lists.  The same
	TechTreeNodeType can appear multiple times in one tree (tier 0, 1, 2 ...).
	tier_index is the 0-based occurrence count of that node type within the tree.
	"""
	lookup: dict[tuple[int, int], tuple[TechTreeNodeType, int]] = {}
	name_to_int = {t.name: t.value for t in TechTreeType}
	for tree_name, tree_data in TECH_TREE_POSITION_LIBRARY.items():
		t_type_int = name_to_int.get(tree_name)
		if t_type_int is None:
			continue
		occurrence: dict[str, int] = {}
		for node in sorted(tree_data["Nodes"], key=lambda n: n["Id"]):
			local_id  = node["Id"]
			type_name = node["Type"]
			try:
				node_type = TechTreeNodeType[type_name]
			except KeyError:
				continue
			tier = occurrence.get(type_name, 0)
			occurrence[type_name] = tier + 1
			lookup[(t_type_int, local_id)] = (node_type, tier)
	return lookup


_TECHTREE_LOOKUP: dict[tuple[int, int], tuple[TechTreeNodeType, int]] = _build_techtree_lookup()


def _parse_secondary_stats_blob(
	stats_blob: str,
	target: SecondaryStatsModel,
	*,
	max_stats: int = _MAX_COLLECTION_STATS,
) -> None:
	"""Parse 20-char tail (2 × 10-char chunks) from collection / equipment lines."""
	for s_idx in range(max_stats):
		start = s_idx * _STATS_CHUNK_LEN
		chunk = stats_blob[start : start + _STATS_CHUNK_LEN]
		if chunk == "0000000000" or len(chunk) < _STATS_CHUNK_LEN:
			continue
		try:
			stat_type = SecondaryStatType(int(chunk[1], 16))
			raw_val = int(chunk[2:_STATS_CHUNK_LEN], 16)
		except (ValueError, KeyError):
			continue
		perfection = raw_val / _U32_DENOM if raw_val else 0.0
		target.add_stat(StatModel(stat_type, perfection))

BLOCK_HEADER    = re.compile(r"^\[([A-Z_]+)\]$")
SUMMON_META     = re.compile(r"^([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{16})")
CURRENCY_LINE   = re.compile(r"^[0-9A-Fa-f]{32}$")
TECH_LINE       = re.compile(r"^[0-9A-Fa-f]+$")

# [SKILL_COLLECTION]: "1{s_enum:02X}0{lvl:02X}{shard:02X}{is_eq:02X}{slot:02X}" + 20-char tail = 32 chars
SKILL_COLL_LINE = re.compile(r"^1([0-9A-Fa-f]{2})0([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})([0-9A-Fa-f]{2})[0-9A-Fa-f]{20}$")

# [PET_EGG_COLLECTION] / [MOUNT_COLLECTION]: 1+1+2+28 = 32 chars per line
# Lua format:
#   pets:   "2{rarity:X}{id:02X}" + "{lvl:02X}{exp:02X}{eq:02X}{slot:02X}" + stats_20char
#   eggs:   "3{rarity:X}00"       + "0000{eq:02X}{slot:02X}"               + "0000{seed:016X}"
#   mounts: "4{rarity:X}{id:02X}" + "{lvl:02X}{exp:02X}{eq:02X}00"         + stats_20char
COLLECTION_LINE = re.compile(r"^([0-9A-Fa-f])([0-9A-Fa-f])([0-9A-Fa-f]{2})([0-9A-Fa-f]{28})$")


def parse_dump(text: str) -> PlayerModel:
	return DumpParser().parse(text)


class DumpParser:
	def __init__(self):
		self._handlers: dict[str, Callable[[PlayerModel, list[str]], None]] = {
			"CURRENCY": self._parse_currency,
			"TECH_TREE": self._parse_techtree,
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
		}

	def parse(self, text: str) -> PlayerModel:
		player = PlayerModel()
		for block_name, lines in self._split_blocks(text).items():
			handler = self._handlers.get(block_name)
			if handler:
				handler(player, lines)
		return player

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

	def _parse_meta_line(self, line: str) -> tuple[int, int, int, int] | None:
		"""Return raw (byte1, byte2, seed, asc) without assigning meaning."""
		m = SUMMON_META.match(line)
		if not m:
			return None
		byte1 = int(m.group(1), 16)
		byte2 = int(m.group(2), 16)
		seed  = int(m.group(3), 16)
		asc   = int(line[-1], 16) if len(line) > 20 else 0
		return byte1, byte2, seed, asc

	def _parse_forge_meta(self, player: PlayerModel, lines: list[str]) -> None:
		if not lines:
			return
		raw = self._parse_meta_line(lines[0])
		if not raw:
			return
		# Forge: byte1=count(always 0), byte2=level
		_, level, seed, asc = raw
		player.forge.forge_count = 0
		player.forge.forge_level = level
		player.forge.forge_seed  = seed
		player.forge.ascension_model.current_level = asc

	def _apply_summon_meta(self, summon_model, ascension_model, line: str) -> None:
		raw = self._parse_meta_line(line)
		if not raw:
			return
		# Summon: Lua outputs level first, count second (variable names are swapped in Lua)
		level, count, seed, asc = raw
		summon_model.level = level
		summon_model.count = count
		summon_model.set_seed(seed)
		if ascension_model is not None:
			ascension_model.current_level = asc

	def _parse_skill_meta(self, player: PlayerModel, lines: list[str]) -> None:
		if lines:
			self._apply_summon_meta(
				player.skills.summon_model,
				player.skills.ascension_model,
				lines[0],
			)

	def _parse_pet_meta(self, player: PlayerModel, lines: list[str]) -> None:
		if lines:
			self._apply_summon_meta(
				player.pets.summon_model,
				player.pets.ascension_model,
				lines[0],
			)

	def _parse_mount_meta(self, player: PlayerModel, lines: list[str]) -> None:
		if lines:
			self._apply_summon_meta(
				player.mounts.summon_model,
				player.mounts.ascension_model,
				lines[0],
			)

	def _parse_currency(self, player: PlayerModel, lines: list[str]) -> None:
		amounts: list[int] = []
		for line in lines:
			if not CURRENCY_LINE.match(line):
				continue
			for i in range(0, 32, 8):
				amounts.append(int(line[i : i + 8], 16))
		for ctype in CurrencyType:
			if ctype.value < len(amounts):
				player.currency.set_currency(ctype, amounts[ctype.value])

	def _parse_techtree(self, player: PlayerModel, lines: list[str]) -> None:
		# Lua format: t_type(1 nibble) + local_id(2 nibbles/1 byte) + level(1 nibble)
		# local_id is the position index within TechTreePositionLibrary for that tree,
		# NOT the TechTreeNodeType enum value.
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk[0] in "Ff":
					continue
				try:
					t_type_val = int(chunk[0], 16)
					local_id   = int(chunk[1:3], 16)
					level      = int(chunk[3], 16)
					mapped = _TECHTREE_LOOKUP.get((t_type_val, local_id))
					if mapped is None:
						continue
					node_type, tier = mapped
					# nibble 0 = internal level 0 = UI level 1.
					# Unresearched nodes are absent from the MetaDictionary entirely,
					# so every node that appears has been researched at least once.
					# Store the UI level (nibble + 1) so type_totals directly equals
					# the total levels to multiply by the per-level bonus value.
					player.techtree.set_node_level(node_type, tier, level + 1)
				except (ValueError, KeyError):
					continue

	def _parse_skill_collection(self, player: PlayerModel, lines: list[str]) -> None:
		# Build enum?mapping lookup once per parse call
		enum_to_skill: dict[int, dict] = {data["Enum"]: data for data in SKILL_MAPPING.values()}
		for line in lines:
			m = SKILL_COLL_LINE.match(line)
			if not m:
				continue
			s_enum  = int(m.group(1), 16)  # CombatSkill enum value (full byte)
			lvl     = int(m.group(2), 16)
			shards  = int(m.group(3), 16)
			is_eq   = int(m.group(4), 16) != 0
			slot    = int(m.group(5), 16)
			data = enum_to_skill.get(s_enum)
			if data is None:
				continue
			rarity = Rarity(data["Rarity"])
			idx    = data["Idx"]
			skill  = SkillModel(rarity, idx)
			skill.level       = lvl
			skill.shard_count = shards
			skill.is_equipped = is_eq
			skill.equip_slot  = slot if is_eq else 0xFF
			player.skills.skills[skill.combat_skill] = skill

	def _parse_pet_egg_collection(self, player: PlayerModel, lines: list[str]) -> None:
		for line in lines:
			m = COLLECTION_LINE.match(line)
			if not m:
				continue
			kind = m.group(1)
			prog = m.group(4)
			if kind == "2":
				rarity = Rarity(int(m.group(2), 16))
				pet_id = int(m.group(3), 16)
				pet = PetModel(pet_id, rarity)
				pet.level = int(prog[0:2], 16)
				pet.experience = int(prog[2:4], 16)
				pet.is_equipped = int(prog[4:6], 16) != 0
				pet.equip_slot = int(prog[6:8], 16)
				_parse_secondary_stats_blob(prog[8:28], pet.secondary_stats)
				player.pets.add_pet(pet)
			elif kind == "3":
				rarity = Rarity(int(m.group(2), 16))
				# prog layout (28 chars): 0000{eq:02X}{slot:02X} + 0000{seed:016X}
				egg = EggModel(rarity, int(prog[12:28], 16))
				egg.is_equipped = int(prog[4:6], 16) != 0
				egg.equip_slot  = int(prog[6:8], 16)
				player.pets.add_egg(egg)

	def _parse_mount_collection(self, player: PlayerModel, lines: list[str]) -> None:
		for line in lines:
			m = COLLECTION_LINE.match(line)
			if not m or m.group(1) != "4":
				continue
			rarity = Rarity(int(m.group(2), 16))
			mount_id = int(m.group(3), 16)
			prog = m.group(4)
			mount = MountModel(mount_id, rarity)
			mount.level = int(prog[0:2], 16)
			mount.experience = int(prog[2:4], 16)
			mount.is_equipped = int(prog[4:6], 16) != 0
			_parse_secondary_stats_blob(prog[8:28], mount.secondary_stats)
			player.mounts.add_mount(mount)

	def _parse_hidden_levels(self, player: PlayerModel, lines: list[str]) -> None:
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk[0] in "Ff" or chunk.upper() == "F000":
					continue
				try:
					item_type = ItemType(int(chunk[0], 16))
					age = int(chunk[1], 16)
					level = int(chunk[2:4], 16)
					player.equipment.set_hidden_level(item_type, age, level)
				except (ValueError, KeyError):
					continue

	def _parse_round_robin(self, player: PlayerModel, lines: list[str]) -> None:
		for line in lines:
			pos = 0
			while pos + 4 <= len(line):
				chunk = line[pos : pos + 4]
				pos += 4
				if chunk == "0000":
					continue
				try:
					item_type = ItemType(int(chunk[0], 16))
					age = int(chunk[1], 16)
					bitmask = int(chunk[2:4], 16)
					indices = [i for i in range(8) if bitmask & (1 << i)]
					player.equipment.set_round_robin(item_type, age, indices)
				except (ValueError, KeyError):
					continue

	def _parse_equipment(self, player: PlayerModel, lines: list[str]) -> None:
		slot_order = list(ItemType)
		for slot_idx, line in enumerate(lines):
			if len(line) < 32 or line.startswith("00000000"):
				continue
			age = int(line[1], 16)
			item_type = ItemType(int(line[2], 16))
			idx = int(line[3], 16)
			level = int(line[4:6], 16)
			item = ItemModel(ItemAge(age), item_type, idx)
			item.level = level
			stats_end = 12 + _EQUIPMENT_STATS_BLOB_LEN
			if len(line) >= stats_end:
				stats_blob = line[12:stats_end]
				max_stats = _MAX_EQUIPMENT_STATS
			else:
				stats_blob = line[12:32]
				max_stats = _MAX_COLLECTION_STATS
			_parse_secondary_stats_blob(
				stats_blob,
				item.secondary_stats,
				max_stats=max_stats,
			)
			if slot_idx < len(slot_order):
				player.equipment.equip_item(item)
