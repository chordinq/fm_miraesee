"""Presentation localization — IL: Localizer.GetTranslation (format layer only)."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from utils.paths import assets_dir

_LOCALIZATIONS_DIR = assets_dir() / "localizations"
_DEFAULT_LANGUAGE = "en"
_LOCALE_FILE = re.compile(r"^.+\(([^)]+)\)\.json$")


@lru_cache(maxsize=1)
def _shared_key_to_id() -> dict[str, dict[str, str]]:
	tables: dict[str, dict[str, str]] = {}
	for path in _LOCALIZATIONS_DIR.glob("* Shared Data.json"):
		table = path.name.replace(" Shared Data.json", "")
		data = json.loads(path.read_text(encoding="utf-8"))
		tables[table] = {
			entry["m_Key"]: str(entry["m_Id"]) for entry in data.get("m_Entries", [])
		}
	return tables


@lru_cache(maxsize=64)
def _load_table(language: str, table: str) -> dict[str, str]:
	mapping: dict[str, str] = {}
	for lang in (language, _DEFAULT_LANGUAGE):
		path = _LOCALIZATIONS_DIR / f"{table}_{lang}.json"
		if not path.is_file():
			continue
		data = json.loads(path.read_text(encoding="utf-8"))
		for entry in data.get("m_TableData", []):
			mapping[str(entry["m_Id"])] = entry["m_Localized"]
		if mapping:
			break
	return mapping


def get_translation(
	loc_key: str,
	*,
	table: str = "General",
	language: str = _DEFAULT_LANGUAGE,
) -> str:
	"""IL: LocalizerBase.GetTranslation(locKey).

	`loc_key` is the Unity localization entry key (e.g. ``"Lv"``, ``"Level"``),
	not the numeric ``m_Id``.
	"""
	if not loc_key:
		return ""
	loc_id = _shared_key_to_id().get(table, {}).get(loc_key, "")
	if not loc_id:
		return loc_key
	text = _load_table(language, table).get(loc_id)
	if text is None:
		return loc_key
	return text


def format_localized(pattern: str, *args: object, language: str = _DEFAULT_LANGUAGE) -> str:
	"""Apply ``string.Format``-style ``{0}`` placeholders after optional loc resolve."""
	text = pattern
	for index, arg in enumerate(args):
		text = text.replace(f"{{{index}}}", str(arg))
	return text
