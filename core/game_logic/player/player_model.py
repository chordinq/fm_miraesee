from ..enums import *
from .player_currency_model import PlayerCurrencyModel
from .player_forge_model import PlayerForgeModel
from .player_equipment_model import PlayerEquipmentModel
from .player_skill_collection_model import PlayerSkillCollectionModel
from .player_techtree_model import PlayerTechTreeModel
from .player_pet_collection_model import PlayerPetCollectionModel
from .player_mount_collection_model import PlayerMountCollectionModel

class PlayerModel:
	def __init__(self):
		self.player_currency_model = PlayerCurrencyModel()
		self.player_forge_model = PlayerForgeModel()
		self.player_equipment_model = PlayerEquipmentModel()
		self.player_skill_collection_model = PlayerSkillCollectionModel()
		self.player_techtree_model = PlayerTechTreeModel()
		self.player_pet_collection_model = PlayerPetCollectionModel()
		self.player_mount_collection_model = PlayerMountCollectionModel()
