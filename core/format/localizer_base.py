"""IL: LocalizerBase + LocalizationSettings selected locale (assets/localizations only)."""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

from utils.paths import assets_dir

_LOCALIZATIONS_DIR = assets_dir() / "localizations"
_DEFAULT_LANGUAGE = "en"
_LOCALE_FILE = re.compile(r"^.+\(([^)]+)\)\.json$")
_selected_language = _DEFAULT_LANGUAGE

_NATIVE_LANGUAGE_LABELS: dict[str, str] = {
	"en": "English",
	"de": "Deutsch",
	"ja": "日本語",
	"ko": "한국어",
	"fr": "français",
	"es": "español",
	"pt-BR": "português (Brasil)",
	"it": "italiano",
	"ru": "русский",
	"tr-TR": "Türkçe (Türkiye)",
	"ar": "العربية",
	"nl": "Nederlands",
	"pl": "Polski",
	"th": "ไทย",
	"zh-CN": "简体中文",
	"zh-TW": "繁體中文",
}


def localizations_dir() -> Path:
	return _LOCALIZATIONS_DIR


def default_language() -> str:
	return _DEFAULT_LANGUAGE


def selected_language() -> str:
	"""IL: LocalizationSettings.GetSelectedLocale identifier code."""
	return _selected_language


def set_selected_language(code: str) -> None:
	"""IL: LocalizationSettings.SetSelectedLocale."""
	global _selected_language
	if code:
		_selected_language = code


def is_english(*, language: str | None = None) -> bool:
	"""IL: Localizer.IsEnglish."""
	return resolve_language(language) == "en"


def resolve_language(language: str | None = None) -> str:
	if language is None or language == "":
		return _selected_language
	return language


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


def loc_id_for_key(table: str, key: str) -> str:
	return _shared_key_to_id().get(table, {}).get(key, "")


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


def load_shared_loc_ids() -> dict[str, dict[str, str]]:
	return _shared_key_to_id()


def clear_localization_cache() -> None:
	_load_table.cache_clear()


def _native_language_label(code: str, fallback: str) -> str:
	return _NATIVE_LANGUAGE_LABELS.get(code, fallback)


def load_available_languages() -> list[dict[str, str]]:
	languages: list[dict[str, str]] = []
	for path in sorted(_LOCALIZATIONS_DIR.glob("*.json")):
		match = _LOCALE_FILE.match(path.name)
		if not match:
			continue
		data = json.loads(path.read_text(encoding="utf-8"))
		code = data.get("m_Identifier", {}).get("m_Code") or match.group(1)
		raw_label = data.get("m_LocaleName") or code
		suffix = f" ({code})"
		fallback = raw_label[: -len(suffix)] if raw_label.endswith(suffix) else raw_label
		label = _native_language_label(code, fallback)
		sort_order = int(data.get("m_SortOrder", 9999))
		languages.append({"code": code, "label": label, "sortOrder": sort_order})
	languages.sort(key=lambda row: (row["sortOrder"], row["label"]))
	return [{"code": row["code"], "label": row["label"]} for row in languages]


def get_translation(
	loc_key: str,
	*,
	table: str = "General",
	language: str | None = None,
) -> str:
	"""IL: LocalizerBase.GetTranslation(locKey) — uses SelectedLocale when language omitted."""
	if not loc_key:
		return ""
	loc_id = _shared_key_to_id().get(table, {}).get(loc_key, "")
	if not loc_id:
		return loc_key
	return get_localized(loc_id, table=table, language=language)


def localize(
	loc_key: str,
	*args: object,
	table: str = "General",
	language: str | None = None,
) -> str:
	"""IL: LocalizerBase.Localize(locKey, formatArg…)."""
	if not loc_key:
		return ""
	loc_id = _shared_key_to_id().get(table, {}).get(loc_key, "")
	if not loc_id:
		text = loc_key
	else:
		text = get_localized(loc_id, table=table, language=language)
	for index, arg in enumerate(args):
		text = text.replace(f"{{{index}}}", str(arg))
	return text


def get_localized(
	loc_id: str,
	*,
	table: str = "General",
	language: str | None = None,
	args: tuple[object, ...] | list[object] | None = None,
) -> str:
	"""Resolve Unity ``m_Id`` string to localized text."""
	if not loc_id:
		return ""
	table_data = _load_table(resolve_language(language), table)
	text = table_data.get(str(loc_id))
	if text is None:
		return ""
	if args:
		for index, arg in enumerate(args):
			text = text.replace(f"{{{index}}}", str(arg))
	return text


def format_localized(pattern: str, *args: object, language: str | None = None) -> str:
	del language
	text = pattern
	for index, arg in enumerate(args):
		text = text.replace(f"{{{index}}}", str(arg))
	return text
