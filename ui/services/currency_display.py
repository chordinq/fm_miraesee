# ui/services/currency_display.py — per-tab summon currency for collection sub-headers
from __future__ import annotations

from core.enums import CurrencyType
from core.game_logic.player_model.PlayerModel import PlayerModel
# One wallet icon per collection tab (matches in-game summon cost).
TAB_CURRENCY: dict[str, CurrencyType] = {
    "skill": CurrencyType.SkillSummonTickets,
    "pet": CurrencyType.Eggshells,
    "mount": CurrencyType.ClockWinders,
}


def tab_currency_row(
    player: PlayerModel, currency: CurrencyType
) -> list[tuple[CurrencyType, int]]:
    return [(currency, player.get_currency(currency))]


def format_currency_amount(amount: int) -> str:
    """Exact wallet balance (no k/M abbreviation)."""
    return str(int(amount))
