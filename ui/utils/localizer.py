import json
from pathlib import Path

from PySide6.QtCore import QObject, Slot

from config import GENERAL_MAPPING
from core.game_logic.enums import AscensionLevel

LOCALIZATIONS_DIR = Path(__file__).resolve().parents[2] / "assets" / "localizations"


def name_loc_from_entry(entry: dict) -> tuple[str, str]:
    loc = entry["Localization"][0]
    return str(loc["Id"]), loc["File"]


def desc_loc_from_entry(entry: dict) -> tuple[str, str]:
    loc = entry["DescLocalization"][0]
    return str(loc["Id"]), loc["File"]


def rarity_loc_from_rarity(rarity: int) -> tuple[str, str]:
    entry = GENERAL_MAPPING["Rarity"].get(str(rarity))
    if entry is None:
        return "", "General"
    loc = entry["Localization"][0]
    return str(loc["Id"]), loc["File"]


def ascension_loc_from_level(level: AscensionLevel) -> tuple[str, str]:
    asc = GENERAL_MAPPING["AscensionLevel"].get(str(int(level.value)))
    if asc is None:
        return "", "General"
    loc = asc["Localization"][0]
    return str(loc["Id"]), loc["File"]


class LocalizationManager(QObject):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._cache: dict[str, dict[str, str]] = {}

    def _load_table(self, language: str, table: str) -> dict[str, str]:
        cache_key = f"{table}_{language}"
        cached = self._cache.get(cache_key)
        if cached is not None:
            return cached

        path = LOCALIZATIONS_DIR / f"{table}_{language}.json"
        mapping: dict[str, str] = {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data["m_TableData"]:
                mapping[str(entry["m_Id"])] = entry["m_Localized"]
        except OSError as exc:
            print(f"Localization load error ({path}): {exc}")
        except (KeyError, json.JSONDecodeError, TypeError) as exc:
            print(f"Localization parse error ({path}): {exc}")

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
        if text is None:
            print(f"[Localizer] missing: {loc_id} in {table}_{language}")
            return ""
        for index, arg in enumerate(args):
            text = text.replace(f"{{{index}}}", str(arg))
        return text


def register_loc_manager(engine) -> LocalizationManager:
    instance = LocalizationManager(parent=engine)
    engine.rootContext().setContextProperty("LocManager", instance)
    return instance
