"""PlayerSkinCollectionModel — ported from IL.

C# PlayerModel fields:
    +0x290  PlayerSkinCollectionModel

C# PlayerSkinCollectionModel fields:
    +0x10  MetaDictionary<ItemType, List<PlayerSkinModel>>   Skins
    +0x18  MetaDictionary<ItemType, PlayerSkinModel>         ObsoleteAfterMigration22To23
    +0x20  MetaDictionary<ItemType, Guid>                    EquippedSkinGuids
    +0x28  MetaDictionary<ItemType, bool>                    SkinVisibility
    +0x30  ulong                                             SkinsRandomSeed

C# PlayerSkinModel fields:
    +0x10/0x18  Guid               (not stored in dump — is_equipped flag used instead)
    +0x20       SkinId             (reference type → ItemType at +0x10, Idx at +0x14)
    +0x28       StatContributions  (reference type → MetaDictionary at +0x10)
    +0x30       int Level
    +0x34       int Experience
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from core.metaplaymath.f64 import f64_from_raw, f64_lerp_raw_from_t_raw

from ..enums import ItemType
from ..stats import StatContribution
from ..stats.stat_helper import StatHelper

if TYPE_CHECKING:
	pass

_STATS_CHUNK_LEN = 10


@dataclass(frozen=True)
class SkinId:
	"""C# Game.Logic.SkinId — keyed by (ItemType, Idx) in SkinsLibrary."""

	item_type: ItemType
	idx: int


@dataclass
class PlayerSkinModel:
	"""C# Game.Logic.PlayerSkinModel (implements ISetPiece).

	IL field offsets:
	    +0x20  SkinId reference (ItemType at +0x10, Idx at +0x14)
	    +0x28  StatContributions
	    +0x30  Level (int)
	    +0x34  Experience (int)
	"""

	skin_id: SkinId
	level: int = 0
	experience: int = 0
	stats_blob: str = ""  # raw 20-char hex blob from StatContributions dict
	is_equipped: bool = False


class PlayerSkinCollectionModel:
	"""IL: Game.Logic.PlayerSkinCollectionModel."""

	def __init__(self) -> None:
		# MetaDictionary<ItemType, List<PlayerSkinModel>>
		self.skins: dict[ItemType, list[PlayerSkinModel]] = {}
		# MetaDictionary<ItemType, bool>
		self.skin_visibility: dict[ItemType, bool] = {}
		self.skins_random_seed: int = 0

	def get_equipped_skins(self) -> dict[ItemType, PlayerSkinModel]:
		"""IL: PlayerSkinCollectionModel.get_EquippedSkins

		Returns the first equipped skin per ItemType slot.
		(C# uses EquippedSkinGuids + GUID matching; we track is_equipped directly.)
		"""
		result: dict[ItemType, PlayerSkinModel] = {}
		for item_type, skin_list in self.skins.items():
			for skin in skin_list:
				if skin.is_equipped:
					result[item_type] = skin
					break
		return result

	def try_get_equipped_skin(self, item_type: ItemType) -> PlayerSkinModel | None:
		"""IL: PlayerSkinCollectionModel.TryGetEquippedSkin"""
		for skin in self.skins.get(item_type, []):
			if skin.is_equipped:
				return skin
		return None


# ── SkinExtensions ────────────────────────────────────────────────────────────


def parse_skin_stat_rolls(stats_blob: str, *, max_stats: int = 2) -> dict[int, int]:
	"""Parse skin StatContributions blob: index nibble + F64 interpolation raw."""
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


def is_good_skin(skin_id: SkinId) -> bool:
	"""IL: SkinExtensions.IsGoodSkin — SkinId.Idx < 100."""
	return skin_id.idx < 100


def stat_increase_per_level(skin_id: SkinId, game_config: Any) -> float:
	"""IL: SkinUpgradeLibrary[ItemType] — Good/Bad increment by IsGoodSkin."""
	upgrade_library = getattr(game_config, "skin_upgrade_library", None)
	if upgrade_library is None:
		return 0.0
	upgrade = upgrade_library.get(skin_id.item_type.name)
	if upgrade is None:
		return 0.0
	if is_good_skin(skin_id):
		return float(upgrade.get("GoodSkinStatIncreasePerLevel", 0.0))
	return float(upgrade.get("BadSkinStatIncreasePerLevel", 0.0))


def _lookup_skin_config(skin_id: SkinId, game_config: Any) -> dict | None:
	skins_library = getattr(game_config, "skins_library", None)
	if skins_library is None:
		return None
	return skins_library.get(skin_id)


def get_base_skin_stat_contributions(
	skin_model: PlayerSkinModel,
	game_config: Any,
) -> list[StatContribution]:
	"""Roll PossibleStats from dump blob into base StatContributions (pre-level)."""
	skin_config = _lookup_skin_config(skin_model.skin_id, game_config)
	if skin_config is None:
		return []

	possible_stats = skin_config.get("PossibleStats", [])
	rolls = parse_skin_stat_rolls(skin_model.stats_blob)

	result: list[StatContribution] = []
	for stat_index, t_raw in rolls.items():
		if stat_index < 0 or stat_index >= len(possible_stats):
			continue
		row = possible_stats[stat_index]
		min_value = float(row.get("MinValue", 0.0))
		max_value = float(row.get("MaxValue", 0.0))
		value = f64_from_raw(f64_lerp_raw_from_t_raw(min_value, max_value, t_raw))
		node = StatHelper.parse_stat_node(row["StatNode"])
		result.append(StatContribution(node, value))
	return result


def get_resolved_stat_contributions_for_level(
	skin_model: PlayerSkinModel,
	level: int,
	game_config: Any,
) -> list[StatContribution]:
	"""IL: SkinExtensions.GetResolvedStatContributionsForLevel — base + increment × level."""
	from core.metaplaymath.fd6 import fd6_add_raw, fd6_from_double

	per_level = stat_increase_per_level(skin_model.skin_id, game_config)
	level_bonus = per_level * level
	base = get_base_skin_stat_contributions(skin_model, game_config)

	return [
		StatContribution(
			row.node,
			0.0,
			raw=fd6_add_raw(row.raw, fd6_from_double(level_bonus)),
		)
		for row in base
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
