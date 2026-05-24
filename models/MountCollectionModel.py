# models/MountCollectionModel.py
from configs.enums import AscendableType
from models.MountModel import MountModel
from models.SummonModel import SummonModel
from models.AscensionModel import AscensionModel

class MountCollectionModel:
	def __init__(self):
		self.mounts = []
		
		self.summon_model = SummonModel()
		self.ascension_model = AscensionModel(AscendableType.Mounts)

	def add_mount(self, mount: MountModel):
		self.mounts.append(mount)

	def tolist(self) -> list:
		combined = []
		for mount in self.mounts:
			combined.append({"type": "Mount", "rarity": mount.rarity, "perfection": mount.perfection, "obj": mount})
		combined.sort(key=lambda x: (x["rarity"].value, x["perfection"]), reverse=True)
		return combined