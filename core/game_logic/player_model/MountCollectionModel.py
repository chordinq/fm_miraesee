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

	def _sort_mounts(self) -> None:
		"""Equipped → Rarity (desc) → Lv (desc) → mount_id (FIFO tie-break)."""
		self.mounts.sort(
			key=lambda m: (
				not m.is_equipped,
				-m.rarity.value,
				-m.level,
				m.mount_id,
			)
		)

	def tolist(self) -> list:
		return [
			{
				"type": "Mount",
				"rarity": mount.rarity,
				"perfection": mount.perfection,
				"obj": mount,
			}
			for mount in self.mounts
		]
