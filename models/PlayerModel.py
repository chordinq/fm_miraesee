# models/PlayerModel.py
from configs.enums import *
from models.CurrencyModel import CurrencyModel
from models.TechTreeModel import TechTreeModel
from models.ForgeModel import ForgeModel
from models.EquipmentModel import EquipmentModel
from models.SkillCollectionModel import SkillCollectionModel
from models.PetCollectionModel import PetCollectionModel
from models.MountCollectionModel import MountCollectionModel

class PlayerModel:
	def __init__(self):
		self.currency = CurrencyModel()
		self.techtree = TechTreeModel()
		self.skills = SkillCollectionModel()
		self.pets = PetCollectionModel()
		self.mounts = MountCollectionModel()

	def get_currency(self, currency_type: CurrencyType) -> int:
		return self.currency.get_currency(currency_type)

	def add_currency(self, currency_type: CurrencyType, amount: int):
		self.currency.add_currency(currency_type, amount)

	def sub_currency(self, currency_type: CurrencyType, amount: int) -> bool:
		if self.currency.get_currency(currency_type) >= amount:
			self.currency.sub_currency(currency_type, amount)
			return True
		return False

	def get_tech_level(self, node_type: TechTreeNodeType) -> int:
		return self.techtree.type_totals.get(node_type, 0)

	def get_power(self) -> float:
		base_dmg = 100.0
		return base_dmg