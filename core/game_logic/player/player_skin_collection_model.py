"""PlayerSkinCollectionModel — IL: Game.Logic.PlayerSkinCollectionModel + SkinExtensions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.metaplaymath.f64 import f64_from_raw, f64_mul_raw, f64_to_raw
from core.metaplaymath.fd6 import fd6_add_raw, fd6_from_f64_raw

from ..enums import ItemType
from ..stats import StatContribution, StatContributions
from ..stats.stat_helper import StatHelper

if TYPE_CHECKING:
	from .player_model import PlayerModel

_STATS_CHUNK_LEN = 10


@dataclass(frozen=True)
class Guid:
	"""C# System.Guid — two ulong fields at PlayerSkinModel +0x10/+0x18."""

	low: int = 0
	high: int = 0

	@classmethod
	def empty(cls) -> Guid:
		return cls(0, 0)

	def is_empty(self) -> bool:
		return self.low == 0 and self.high == 0

	@classmethod
	def from_parts(cls, low: int, high: int) -> Guid:
		mask = (1 << 64) - 1
		return cls(low & mask, high & mask)

	@classmethod
	def from_uuid_string(cls, value: str) -> Guid:
		parts = value.split("-", 1)
		if len(parts) != 2:
			raise ValueError(f"invalid skin guid string: {value!r}")
		return cls.from_parts(int(parts[0], 16), int(parts[1], 16))

	def __eq__(self, other: object) -> bool:
		if not isinstance(other, Guid):
			return False
		return self.low == other.low and self.high == other.high


@dataclass(frozen=True)
class SkinId:
	"""C# Game.Logic.SkinId — ItemType at +0x10, Idx at +0x14."""

	item_type: ItemType
	idx: int

	def equals(self, other: SkinId | None) -> bool:
		if other is None:
			return False
		return self.item_type == other.item_type and self.idx == other.idx


@dataclass(frozen=True)
class AdvancedSkinId:
	"""C# Game.Logic.AdvancedSkinId — SkinId + Level."""

	skin_id: SkinId
	level: int


@dataclass
class PlayerSkinModel:
	"""C# Game.Logic.PlayerSkinModel (ISetPiece).

	IL offsets:
	    +0x10/+0x18  Guid
	    +0x20         SkinId
	    +0x28         StatContributions
	    +0x30         Level
	    +0x34         Experience
	"""

	guid: Guid
	skin_id: SkinId
	stat_contributions: StatContributions
	level: int = 0
	experience: int = 0


class PlayerSkinCollectionModel:
	"""IL: Game.Logic.PlayerSkinCollectionModel."""

	def __init__(self) -> None:
		self.skins: dict[ItemType, list[PlayerSkinModel]] = {}
		self.obsolete_after_migration_22_to_23: dict[ItemType, PlayerSkinModel] = {}
		self.equipped_skin_guids: dict[ItemType, Guid] = {}
		self.skin_visibility: dict[ItemType, bool] = {}
		self.skins_random_seed: int = 0

	def init(self, skins_random_seed: int) -> None:
		"""IL: PlayerSkinCollectionModel.Init — seed + default dict entries per ItemType."""
		self.skins_random_seed = skins_random_seed
		for item_type in ItemType:
			if item_type not in self.skins:
				self.skins[item_type] = []
			if item_type not in self.equipped_skin_guids:
				self.equipped_skin_guids[item_type] = Guid.empty()
			if item_type not in self.skin_visibility:
				self.skin_visibility[item_type] = True

	@property
	def equipped_skins(self) -> dict[ItemType, PlayerSkinModel]:
		return self.get_equipped_skins()

	def get_equipped_skins(self) -> dict[ItemType, PlayerSkinModel]:
		"""IL: get_EquippedSkins — EquippedSkinGuids → TryGetEquippedSkin per slot."""
		result: dict[ItemType, PlayerSkinModel] = {}
		for item_type in self.equipped_skin_guids:
			found, skin = self.try_get_equipped_skin(item_type)
			if found and skin is not None:
				result[item_type] = skin
		return result

	def try_get_equipped_skin(
		self,
		item_type: ItemType,
	) -> tuple[bool, PlayerSkinModel | None]:
		"""IL: TryGetEquippedSkin — GUID match in slot list, skip empty equipped GUID."""
		guid = self.equipped_skin_guids.get(item_type, Guid.empty())
		if guid.is_empty():
			return False, None
		skin = self._find_skin_by_guid(item_type, guid)
		if skin is None:
			return False, None
		return True, skin

	def get_equipped_skin(self, item_type: ItemType) -> PlayerSkinModel | None:
		"""IL: GetEquippedSkin."""
		_, skin = self.try_get_equipped_skin(item_type)
		return skin

	def equip_skin(self, to_equip: PlayerSkinModel) -> PlayerSkinModel | None:
		"""IL: EquipSkin — store GUID, return previously equipped skin in slot."""
		item_type = to_equip.skin_id.item_type
		previous_guid = self.equipped_skin_guids.get(item_type, Guid.empty())
		auto_unequipped: PlayerSkinModel | None = None
		if not previous_guid.is_empty():
			auto_unequipped = self._find_skin_by_guid(item_type, previous_guid)
		self.equipped_skin_guids[item_type] = to_equip.guid
		return auto_unequipped

	def skin_id_count(self, skin_id: SkinId) -> int:
		"""IL: SkinIdCount — count skins in slot matching SkinId."""
		return sum(
			1
			for skin in self.skins.get(skin_id.item_type, [])
			if skin.skin_id.equals(skin_id)
		)

	def get_visible_skins(self) -> dict[ItemType, AdvancedSkinId]:
		"""IL: GetVisibleSkins — equipped skins where SkinVisibility[slot] is true."""
		result: dict[ItemType, AdvancedSkinId] = {}
		for item_type, skin in self.get_equipped_skins().items():
			if not self.skin_visibility.get(item_type, True):
				continue
			result[item_type] = to_advanced_skin_id(skin)
		return result

	def _find_skin_by_guid(
		self,
		item_type: ItemType,
		guid: Guid,
	) -> PlayerSkinModel | None:
		for skin in self.skins.get(item_type, []):
			if skin.guid == guid:
				return skin
		return None


def parse_skin_stat_rolls(stats_blob: str, *, max_stats: int = 2) -> dict[int, int]:
	"""Parse skin StatContributions dump blob: index nibble + F64 interpolation raw."""
	rolls: dict[int, int] = {}
	for index in range(max_stats):
		start = index * _STATS_CHUNK_LEN
		chunk = stats_blob[start : start + _STATS_CHUNK_LEN]
		if chunk == "0000000000" or len(chunk) < _STATS_CHUNK_LEN:
			continue
		if chunk[0] != "1":
			continue
		stat_index = int(chunk[1], 16)
		raw = int(chunk[2:_STATS_CHUNK_LEN], 16)
		if raw == 0:
			continue
		rolls[stat_index] = raw
	return rolls


def _wire_raw_to_f64(raw_u32: int) -> float:
	if raw_u32 >= 0x80000000:
		raw_u32 -= 0x100000000
	return f64_from_raw(raw_u32)


def build_stat_contributions_from_dump_blob(
	skin_id: SkinId,
	stats_blob: str,
	game_config: Any,
) -> list[StatContribution]:
	"""Reconstruct base StatContributions from exporter stats blob (dump ingest only)."""
	skin_config = _lookup_skin_config(skin_id, game_config)
	if skin_config is None:
		return []

	possible_stats = skin_config.get("PossibleStats", [])
	rolls = parse_skin_stat_rolls(stats_blob)

	result: list[StatContribution] = []
	for stat_index, raw_u32 in rolls.items():
		if stat_index < 0 or stat_index >= len(possible_stats):
			continue
		row = possible_stats[stat_index]
		value = _wire_raw_to_f64(raw_u32)
		node = StatHelper.parse_stat_node(row["StatNode"])
		result.append(StatContribution(node, value))
	return result


def deterministic_dump_guid(item_type: ItemType, idx: int, ordinal: int) -> Guid:
	"""Stable GUID for dump reload when runtime memory GUID is not exported."""
	low = (int(item_type) << 32) | ((idx & 0xFFFF) << 16) | (ordinal & 0xFFFF)
	return Guid.from_parts(low, 0xD000000000000001)


def is_good_skin(skin_id: SkinId) -> bool:
	"""IL: SkinExtensions.IsGoodSkin — SkinId.Idx < 100."""
	return skin_id.idx < 100


def stat_increase_per_level(skin_id: SkinId, game_config: Any) -> float:
	"""IL: SkinExtensions.StatIncreasePerLevel — SkinUpgradeLibrary[slot ItemType]."""
	upgrade_library = getattr(game_config, "skin_upgrade_library", None)
	if upgrade_library is None:
		raise ValueError(
			"skin_upgrade_library is required for SkinExtensions.StatIncreasePerLevel"
		)
	upgrade = upgrade_library.get(skin_id.item_type.name)
	if upgrade is None:
		raise ValueError(
			f"skin upgrade config not found for {skin_id.item_type.name!r}"
		)
	if is_good_skin(skin_id):
		return float(upgrade.get("GoodSkinStatIncreasePerLevel", 0.0))
	return float(upgrade.get("BadSkinStatIncreasePerLevel", 0.0))


def get_resolved_stat_contributions_for_level(
	skin_model: PlayerSkinModel,
	level: int,
	game_config: Any,
) -> list[StatContribution]:
	"""IL: SkinExtensions.GetResolvedStatContributionsForLevel."""
	per_level_raw = f64_to_raw(stat_increase_per_level(skin_model.skin_id, game_config))
	level_bonus_raw = f64_mul_raw(per_level_raw, f64_to_raw(float(level)))
	level_bonus_fd6 = fd6_from_f64_raw(level_bonus_raw)

	return [
		StatContribution(
			row.node,
			0.0,
			raw=fd6_add_raw(row.raw, level_bonus_fd6),
		)
		for row in skin_model.stat_contributions.stats
	]


def get_resolved_stat_contributions(
	skin_model: PlayerSkinModel,
	game_config: Any,
) -> list[StatContribution]:
	"""IL: SkinExtensions.GetResolvedStatContributions."""
	return get_resolved_stat_contributions_for_level(
		skin_model,
		skin_model.level,
		game_config,
	)


def to_advanced_skin_id(skin_model: PlayerSkinModel) -> AdvancedSkinId:
	"""IL: SkinExtensions.ToAdvancedSkinId."""
	return AdvancedSkinId(skin_id=skin_model.skin_id, level=skin_model.level)


def is_max_level(skin_model: PlayerSkinModel, game_config: Any) -> bool:
	"""IL: SkinExtensions.IsMaxLevel(PlayerSkinModel)."""
	return is_max_level_for_skin_id(
		skin_model.skin_id,
		skin_model.level,
		game_config,
	)


def is_max_level_for_skin_id(
	skin_id: SkinId,
	level: int,
	game_config: Any,
) -> bool:
	"""IL: SkinExtensions.IsMaxLevel(SkinId, level)."""
	return level >= get_max_level(skin_id, game_config)


def is_max_level_for_advanced_skin_id(
	advanced_skin_id: AdvancedSkinId,
	game_config: Any,
) -> bool:
	"""IL: SkinExtensions.IsMaxLevel(AdvancedSkinId)."""
	return is_max_level_for_skin_id(
		advanced_skin_id.skin_id,
		advanced_skin_id.level,
		game_config,
	)


def get_max_level(skin_id: SkinId, game_config: Any) -> int:
	"""IL: SkinExtensions.GetMaxLevel — experience table length − 1."""
	experience_table = _skin_experience_table(skin_id, game_config)
	if not experience_table:
		return 0
	return len(experience_table) - 1


def is_equipped(skin: PlayerSkinModel, player: PlayerModel) -> bool:
	"""IL: SkinExtensions.IsEquipped — EquippedSkinGuids[slot] == skin.Guid."""
	collection = player.player_skin_collection_model
	item_type = skin.skin_id.item_type
	equipped_guid = collection.equipped_skin_guids.get(item_type, Guid.empty())
	return not equipped_guid.is_empty() and equipped_guid == skin.guid


def is_part_of_set(skin_id: SkinId, game_config: Any) -> bool:
	"""IL: SkinExtensions.IsPartOfSet."""
	skin_config = _lookup_skin_config(skin_id, game_config)
	if skin_config is None:
		return False
	base_set_id = skin_config.get("BaseSetId")
	if base_set_id is None:
		return False
	if isinstance(base_set_id, str):
		return base_set_id != ""
	return bool(base_set_id)


def get_base_set_id(skin_id: SkinId, game_config: Any) -> str | None:
	"""IL: SkinExtensions.GetBaseSetId."""
	skin_config = _lookup_skin_config(skin_id, game_config)
	if skin_config is None:
		return None
	base_set_id = skin_config.get("BaseSetId")
	if base_set_id is None or base_set_id == "":
		return None
	return str(base_set_id)


def has_evolutions(skin_id: SkinId, game_config: Any) -> bool:
	"""IL: SkinExtensions.HasEvolutions — not present in 2.6.0 SkinsLibrary export."""
	raise NotImplementedError(
		"SkinExtensions.HasEvolutions — awaiting IL/decompile basis"
	)


def create_skin(
	game_config: Any,
	skin_id: SkinId,
	random: Any,
) -> PlayerSkinModel:
	"""IL: SkinExtensions.CreateSkin."""
	raise NotImplementedError(
		"SkinExtensions.CreateSkin — awaiting full IL port (RandomPCG + GenerateStatsFromRange)"
	)


def _lookup_skin_config(skin_id: SkinId, game_config: Any) -> dict | None:
	skins_library = getattr(game_config, "skins_library", None)
	if skins_library is None:
		return None
	return skins_library.get(skin_id)


def _skin_experience_table(skin_id: SkinId, game_config: Any) -> list[int]:
	upgrade_library = getattr(game_config, "skin_upgrade_library", None)
	if upgrade_library is None:
		raise ValueError("skin_upgrade_library is required for SkinExtensions.GetMaxLevel")
	upgrade = upgrade_library.get(skin_id.item_type.name)
	if upgrade is None:
		raise ValueError(
			f"skin upgrade config not found for {skin_id.item_type.name!r}"
		)
	if is_good_skin(skin_id):
		return list(upgrade.get("GoodSkinsLevelExperience", []))
	return list(upgrade.get("BadSkinsLevelExperience", []))
