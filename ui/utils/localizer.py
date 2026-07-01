import json
import re
from pathlib import Path

from PySide6.QtCore import QObject, Property, Slot

from config import GENERAL_MAPPING
from core.game_logic.enums import AscensionLevel
from utils.paths import assets_dir

LOCALIZATIONS_DIR = assets_dir() / "localizations"
_DEFAULT_LANGUAGE = "en"
_LOCALE_FILE = re.compile(r"^.+\(([^)]+)\)\.json$")


def _loc_block_id(loc: dict) -> str:
    value = loc.get("Id", loc.get("id"))
    return str(value) if value is not None else ""


def name_loc_from_entry(entry: dict) -> tuple[str, str]:
    loc = entry["Localization"][0]
    return _loc_block_id(loc), loc["File"]


def desc_loc_from_entry(entry: dict) -> tuple[str, str]:
    loc = entry["DescLocalization"][0]
    return _loc_block_id(loc), loc["File"]


def rarity_loc_from_rarity(rarity: int) -> tuple[str, str]:
    entry = GENERAL_MAPPING["Rarity"].get(str(rarity))
    if entry is None:
        return "", "General"
    loc = entry["Localization"][0]
    return _loc_block_id(loc), loc["File"]


def ascension_loc_from_level(level: AscensionLevel) -> tuple[str, str]:
    asc = GENERAL_MAPPING["AscensionLevel"].get(str(int(level.value)))
    if asc is None:
        return "", "General"
    loc = asc["Localization"][0]
    return _loc_block_id(loc), loc["File"]


def load_shared_loc_ids() -> dict[str, dict[str, str]]:
    tables: dict[str, dict[str, str]] = {}
    for path in LOCALIZATIONS_DIR.glob("* Shared Data.json"):
        table = path.name.replace(" Shared Data.json", "")
        data = json.loads(path.read_text(encoding="utf-8"))
        tables[table] = {entry["m_Key"]: str(entry["m_Id"]) for entry in data.get("m_Entries", [])}
    return tables


def loc_id_for_key(table: str, key: str) -> str:
    return load_shared_loc_ids().get(table, {}).get(key, "")


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


def _native_language_label(code: str, fallback: str) -> str:
    return _NATIVE_LANGUAGE_LABELS.get(code, fallback)


def load_available_languages() -> list[dict[str, str]]:
    languages: list[dict[str, str]] = []
    for path in sorted(LOCALIZATIONS_DIR.glob("*.json")):
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


AVAILABLE_LANGUAGES = load_available_languages()


class LocalizationManager(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cache: dict[str, dict[str, str]] = {}
        self._languages = AVAILABLE_LANGUAGES

    @Property("QVariantList", constant=True)
    def languages(self) -> list[dict[str, str]]:
        return self._languages

    def _load_table(self, language: str, table: str) -> dict[str, str]:
        cache_key = f"{table}_{language}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        mapping: dict[str, str] = {}
        for lang in (language, _DEFAULT_LANGUAGE):
            path = LOCALIZATIONS_DIR / f"{table}_{lang}.json"
            if not path.exists():
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                for entry in data.get("m_TableData", []):
                    mapping[str(entry["m_Id"])] = entry["m_Localized"]
            except OSError as exc:
                print(f"Localization load error ({path}): {exc}")
            except (KeyError, json.JSONDecodeError, TypeError) as exc:
                print(f"Localization parse error ({path}): {exc}")
            if mapping:
                break

        self._cache[cache_key] = mapping
        return mapping

    @Slot(str, str, str, "QVariantList", result=str)
    def get_string(
        self,
        loc_id: str,
        language: str,
        table: str = "General",
        args: list | None = None,
    ) -> str:
        if not loc_id:
            return ""
        if args is None:
            args = []
        table_data = self._load_table(language, table or "General")
        text = table_data.get(loc_id)
        if text is None and language != _DEFAULT_LANGUAGE:
            text = self._load_table(_DEFAULT_LANGUAGE, table or "General").get(loc_id)
        if text is None:
            print(f"[Localizer] missing: {loc_id} in {table}_{language}")
            return ""
        for index, arg in enumerate(args):
            text = text.replace(f"{{{index}}}", str(arg))
        return text

    @Slot(result=bool)
    def clear_cache(self) -> bool:
        self._cache.clear()
        return True


def register_loc_manager(engine) -> LocalizationManager:
    instance = LocalizationManager(parent=engine)
    engine.rootContext().setContextProperty("LocManager", instance)
    return instance
