"""TMPText inline icons — Image + text rows (CurrencyButton-style)."""
from __future__ import annotations

from config import SPRITES_DIR
from core.format.number_format import format_currency_value, format_power
from core.game_logic.enums import CurrencyType

# Resolved from ui/TMPText/TMPText.qml via Qt.resolvedUrl()
_ICON_REL_PREFIX = "../../assets/sprites/Currency/"

_CURRENCY_FILES: dict[CurrencyType, str] = {
	CurrencyType.Coins: "CoinIcon.png",
	CurrencyType.Gems: "GemIcon.png",
	CurrencyType.Hammers: "hammer.png",
	CurrencyType.SkillSummonTickets: "skillTicket.png",
	CurrencyType.Eggshells: "Eggshells.png",
	CurrencyType.TechPotions: "techPotions.png",
	CurrencyType.PvpTickets: "pvpTicket.png",
	CurrencyType.ClockWinders: "clockWinders.png",
	CurrencyType.WarBattleTickets: "WarTickets.png",
	CurrencyType.Token: "Token.png",
	CurrencyType.MissionEnergy: "Energy.png",
	CurrencyType.GuildPotions: "guildPotions.png",
}


def currency_icon_source(currency_type: CurrencyType) -> str:
	"""Relative path for ``TMPText.iconSource`` → ``Qt.resolvedUrl`` in QML."""
	filename = _CURRENCY_FILES.get(currency_type)
	if filename is None:
		return ""
	path = SPRITES_DIR / "Currency" / filename
	if not path.is_file():
		return ""
	return f"{_ICON_REL_PREFIX}{filename}"


def format_currency_value_text(amount: int | float, currency_type: CurrencyType) -> str:
	_ = currency_type
	return format_currency_value(amount)


def format_currency_line(
	amount: int | float,
	currency_type: CurrencyType,
	*,
	show_icon: bool = True,
) -> tuple[str, str]:
	text = format_currency_value_text(amount, currency_type)
	icon = currency_icon_source(currency_type) if show_icon else ""
	return icon, text


def format_power_line(value: int, *, show_icon: bool = True) -> tuple[str, str]:
	_ = show_icon
	return "", format_power(value)
