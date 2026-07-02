"""Resolve mapping entry keys to localized strings (assets Shared Data only)."""
from __future__ import annotations

from core.game_logic.enums import AscensionLevel, Rarity

from .localizer import get_ascension_name, get_rarity_name
from .localizer_base import get_translation


def localized_name_from_entry(entry: dict, *, language: str = "en") -> str:
	"""Mapping ``Key`` + ``Localization[0].File`` → finished name string."""
	loc = entry["Localization"][0]
	return get_translation(entry["Key"], table=loc["File"], language=language)


def localized_desc_from_entry(entry: dict, *, language: str = "en") -> str:
	"""Skill-style desc: mapping ``Key`` + ``Desc`` suffix on desc table."""
	loc = entry["DescLocalization"][0]
	return get_translation(f"{entry['Key']}Desc", table=loc["File"], language=language)


def loc_id_from_entry(entry: dict, *, desc: bool = False) -> tuple[str, str]:
	"""Legacy AppText: ``(m_Id, table)`` from mapping block (assets table ids)."""
	block = entry["DescLocalization" if desc else "Localization"][0]
	loc_id = block.get("Id", block.get("id"))
	return str(loc_id) if loc_id is not None else "", block["File"]


def rarity_name(rarity: int | Rarity, *, language: str = "en") -> str:
	if isinstance(rarity, Rarity):
		return get_rarity_name(rarity, language=language)
	return get_rarity_name(Rarity(rarity), language=language)


def ascension_name(level: AscensionLevel, *, language: str = "en") -> str:
	return get_ascension_name(level, language=language)


def loc_id_for_key(table: str, key: str) -> str:
	from .localizer_base import loc_id_for_key as _loc_id_for_key

	return _loc_id_for_key(table, key)
