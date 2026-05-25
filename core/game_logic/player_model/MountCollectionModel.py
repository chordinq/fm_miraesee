# models/MountCollectionModel.py
from core.enums import AscendableType
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.SummonModel import SummonModel
from core.game_logic.player_model.AscensionModel import AscensionModel

class MountCollectionModel:
	def __init__(self):
		self.mounts = []
		
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Mounts)

	def add_mount(self, mount: MountModel):
		self.mounts.append(mount)
		self._sort_mounts()

	def _sort_mounts(self):
		self.mounts.sort(
			key=lambda m: (
				not m.is_equipped,
				getattr(m, "equip_slot", 0),
				-m.rarity.value,
				m.mount_id,
			)
		)

	def tolist(self) -> list:
		combined = []
		for mount in self.mounts:
			combined.append({"type": "Mount", "rarity": mount.rarity, "perfection": mount.perfection, "obj": mount})
		combined.sort(key=lambda x: (x["rarity"].value, x["perfection"]), reverse=True)
		return combined