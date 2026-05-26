# models/CurrencyModel.py
from core.enums import CurrencyType

class CurrencyModel:
	def __init__(self):
		self.currencies = {ctype: 0 for ctype in CurrencyType}

	def get_currency(self, currency_type: CurrencyType) -> int:
		return self.currencies.get(currency_type, 0)

	def set_currency(self, currency_type: CurrencyType, amount: int):
		self.currencies[currency_type] = amount

	def add_currency(self, currency_type: CurrencyType, amount: int):
		self.currencies[currency_type] += amount

	def sub_currency(self, currency_type: CurrencyType, amount: int):
		self.currencies[currency_type] -= amount