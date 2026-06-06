from __future__ import annotations

from dataclasses import dataclass

from ..enums import AscendableType, Rarity
from ..stats import SecondaryStats
from .ascension_model import AscensionModel
from .summon_model import SummonModel


@dataclass(frozen=True)
class MountId:
	rarity: Rarity
	id: int


class PlayerMountModel:
	def __init__(
		self,
		guid: str,
		mount_id: MountId,
		secondary_stats: SecondaryStats,
	) -> None:
		# IL .ctor(Guid, MountId, SecondaryStats)
		self.guid = guid
		self.mount_id = mount_id
		self.secondary_stats = secondary_stats
		self.level = 0
		self.experience = 0
		self.is_equipped = False


class PlayerMountCollectionModel:
	def __init__(self) -> None:
		self.player_mount_models: list[PlayerMountModel] = []
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Mounts)

	def ascend(self) -> None:
		self.player_mount_models.clear()
		self.summon_model.reset()
		self.ascension_model.ascend()
