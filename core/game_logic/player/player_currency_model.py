# updated 2026-06-03
from __future__ import annotations

from collections.abc import Callable
from typing import TYPE_CHECKING, Optional

from dataclasses import dataclass

from ..enums import CurrencyType

if TYPE_CHECKING:
	from .player_model import PlayerModel

_negative_currency_policy: Callable[[], bool] | None = None


def register_negative_currency_policy(policy: Callable[[], bool] | None) -> None:
	global _negative_currency_policy
	_negative_currency_policy = policy


def negative_currency_allowed() -> bool:
	if _negative_currency_policy is None:
		return False
	return _negative_currency_policy()


@dataclass
class Price:
    amount: int
    currency: CurrencyType

    def __mul__(self, other: int) -> Price:
        return Price(self.amount * other, self.currency)


class SpendContext:
	def __init__(
		self,
		player_model: "PlayerModel",
		currency_type: CurrencyType,
		spent_amount: int,
	) -> None:
		self._player = player_model
		self._currency_type = currency_type
		self._spent_amount = spent_amount

	def free(self, amount: int) -> None:
		self._spent_amount = max(0, self._spent_amount - amount)

	def can_afford(self) -> bool:
		if negative_currency_allowed():
			return True
		currency_model = self._player.player_currency_model
		return currency_model.can_afford(self._currency_type, self._spent_amount)

	def spend(self, sink_name: str) -> None:
		_ = sink_name
		currency_model = self._player.player_currency_model
		if self._spent_amount < 1:
			currency_model._current_transaction = None
			return
		if currency_model.can_afford(self._currency_type, self._spent_amount):
			currency_model.currencies[self._currency_type] -= self._spent_amount
		elif negative_currency_allowed():
			currency_model.add_or_subtract(self._currency_type, -self._spent_amount)
		else:
			raise ValueError(
				f"Cannot spend {self._spent_amount} {self._currency_type!r}"
			)
		currency_model._current_transaction = None


class PlayerCurrencyModel:
    def __init__(self):
        self.currencies = {ctype: 0 for ctype in CurrencyType}
        self._current_transaction = None

    def create_spend_context(
        self,
        player_model: "PlayerModel",
        currency_type: CurrencyType,
        spent_amount: int,
    ) -> SpendContext:
        context = SpendContext(player_model, currency_type, spent_amount)
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
        if negative_currency_allowed():
            return True
        return self.currencies[currency_type] >= amount
    
    def can_afford_price(self, price: Price) -> bool:
        return self.can_afford(price.currency, price.amount)

    def top_up(self, player_model: PlayerModel, price: Price, amount: int) -> None:
        raise NotImplementedError("not useful for now")

    def add_in_migration(self, currency_type: CurrencyType, amount: int) -> None:
        raise NotImplementedError("not useful for now")

    def reset_currency(self, player_model: PlayerModel, currency_type: CurrencyType) -> None:
        player_model.player_currency_model.currencies[currency_type] = 0


def can_afford(
    player_model: "PlayerModel",
    currency_type: CurrencyType,
    amount: int,
) -> tuple[bool, Optional[SpendContext]]:
    if amount < 0:
        return False, None
    if player_model is None:
        raise ValueError("CurrencyPlayerModelExtensions.CanAfford requires player")
    currency_model = player_model.player_currency_model
    if currency_model is None:
        raise ValueError("CurrencyPlayerModelExtensions.CanAfford requires PlayerCurrencyModel")
    if not currency_model.can_afford(currency_type, amount):
        if not negative_currency_allowed():
            return False, None
    spend_context = currency_model.create_spend_context(
        player_model,
        currency_type,
        amount,
    )
    return True, spend_context
