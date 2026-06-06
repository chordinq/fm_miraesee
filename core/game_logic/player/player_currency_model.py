# updated 2026-06-03
from __future__ import annotations
from typing import TYPE_CHECKING
from dataclasses import dataclass
from ..enums import CurrencyType
if TYPE_CHECKING:
	from .player_model import PlayerModel


@dataclass
class Price:
    amount: int
    currency: CurrencyType

    def __mul__(self, other: int) -> Price:
        return Price(self.amount * other, self.currency)


class SpendContext:
	def __init__(
		self,
		currency_model: "PlayerCurrencyModel",
		currency_type: CurrencyType,
		spent_amount: int,
	) -> None:
		self._currency_model = currency_model
		self._currency_type = currency_type
		self._spent_amount = spent_amount

	def free(self, amount: int) -> None:
		self._spent_amount = max(0, self._spent_amount - amount)

	def can_afford(self) -> bool:
		return self._currency_model.can_afford(self._currency_type, self._spent_amount)

	def spend(self, sink_name: str) -> None:
		if self._spent_amount < 1:
			self._currency_model._current_transaction = None
			return
		self._currency_model.currencies[self._currency_type] -= self._spent_amount
		self._currency_model._current_transaction = None


class PlayerCurrencyModel:
    def __init__(self):
        self.currencies = {ctype: 0 for ctype in CurrencyType}
        self._current_transaction = None

    def create_spend_context(self, currency_type, spent_amount):
        context = SpendContext(self, currency_type, spent_amount)
        self._current_transaction = context
        return context
    
    def add(self, currency_type: CurrencyType, amount: int) -> None:
        if amount < 0:
            raise ValueError("Amount must be positive")
        self.currencies[currency_type] += amount

    def add_or_subtract(self, currency_type: CurrencyType, amount: int) -> None:
        self.currencies[currency_type] += amount

    def get(self, currency_type: CurrencyType) -> int:
        return self.currencies[currency_type]

    def set_currency(self, currency_type: CurrencyType, amount: int) -> None:
        self.currencies[currency_type] = amount

    def can_afford(self, currency_type: CurrencyType, amount: int) -> bool:
        return self.currencies[currency_type] >= amount
    
    def can_afford_price(self, price: Price) -> bool:
        return self.can_afford(price.currency, price.amount)

    def top_up(self, player_model: PlayerModel, price: Price, amount: int) -> None:
        raise NotImplementedError("not useful for now")

    def add_in_migration(self, currency_type: CurrencyType, amount: int) -> None:
        raise NotImplementedError("not useful for now")

    def reset_currency(self, player_model: PlayerModel, currency_type: CurrencyType) -> None:
        player_model.player_currency_model.currencies[currency_type] = 0
