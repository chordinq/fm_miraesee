"""IL: Localizer static facades — GeneralLocalizer, cross-cutting loc helpers."""
from __future__ import annotations

from core.game_logic.enums import (
	AscensionLevel,
	CurrencyType,
	DungeonType,
	Rarity,
)

from .localizer_base import get_translation, localize

_DUNGEON_TITLE_SUFFIX = "DungeonTitle"
_BRACKET_OPEN = "["
_BRACKET_CLOSE = "] "


def get_rarity_name(rarity: Rarity, *, language: str | None = None) -> str:
	"""IL: GeneralLocalizer.GetRarityName / RarityExtensions.GetLocalizedString."""
	return get_translation(rarity.name, table="General", language=language)


def get_currency_name(currency: CurrencyType, *, language: str | None = None) -> str:
	"""IL: GeneralLocalizer.GetCurrencyName."""
	return get_translation(currency.name, table="General", language=language)


def get_ascension_name(level: AscensionLevel, *, language: str | None = None) -> str:
	if level == AscensionLevel.None_:
		return ""
	return get_translation(level.name, table="General", language=language)


def get_dungeon_name(dungeon: DungeonType, *, language: str | None = None) -> str:
	"""IL: DungeonsLocalizer.GetDungeonName — ``{Enum}DungeonTitle``."""
	loc_key = f"{dungeon.name}{_DUNGEON_TITLE_SUFFIX}"
	return get_translation(loc_key, table="Dungeons", language=language)


def format_bracketed_entity_title(
	rarity: Rarity,
	name: str,
	*,
	language: str | None = None,
) -> str:
	"""IL: ``[{rarity}] {name}`` without StringExtensions.Colorize."""
	rarity_text = get_rarity_name(rarity, language=language)
	return f"{_BRACKET_OPEN}{rarity_text}{_BRACKET_CLOSE}{name}"


def get_dungeon_drop_text(
	dungeon: DungeonType,
	currency: CurrencyType | None = None,
	*,
	language: str | None = None,
) -> str:
	"""IL: StatsLocalizer.GetDungeonDropText — ``Stats.XDungeonDropY``."""
	from .stats_localizer import get_dungeon_drop_text as _get_dungeon_drop_text

	return _get_dungeon_drop_text(dungeon, currency, language=language)
