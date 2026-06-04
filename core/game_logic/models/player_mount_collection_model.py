from __future__ import annotations
from dataclasses import dataclass
from uuid import uuid4
from ..enums import Rarity, AscendableType
from ..stats import SecondaryStats
from .summon_model import SummonModel
from .ascension_model import AscensionModel

@dataclass(frozen=True)
class MountId:
	rarity: Rarity
	id: int

class PlayerMountModel:
	def __init__(self,
		mount_id: MountId,
		level: int = 0,
		experience: int = 0,
		is_equipped: bool = False,
		equip_slot: int = 0,
		secondary_stats: SecondaryStats = SecondaryStats(),
	) -> None:
		self.guid = str(uuid4())
		self.mount_id = mount_id
		self.level = level
		self.experience = experience
		self.is_equipped = is_equipped
		self.equip_slot = equip_slot
		self.secondary_stats = secondary_stats

	@property
	def perfection(self) -> float:
		return self.secondary_stats.perfection

class PlayerMountCollectionModel:
	def __init__(self) -> None:
		self.player_mount_models: list[PlayerMountModel] = []
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Mounts)

	def ascend(self) -> None:
		self.player_mount_models.clear()
		self.summon_model.reset()
		self.ascension_model.ascend()
