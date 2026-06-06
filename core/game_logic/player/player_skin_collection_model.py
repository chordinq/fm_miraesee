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
from typing import TYPE_CHECKING

from ..enums import ItemType

if TYPE_CHECKING:
	pass


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
