from PySide6.QtCore import QObject, Property, Slot

from core.format.localizer_base import (
	clear_localization_cache,
	get_localized,
	load_available_languages,
	localizations_dir,
	loc_id_for_key as core_loc_id_for_key,
	resolve_language,
)
from core.format.mapping_loc import loc_id_from_entry

LOCALIZATIONS_DIR = localizations_dir()
AVAILABLE_LANGUAGES = load_available_languages()


def name_loc_from_entry(entry: dict) -> tuple[str, str]:
	return loc_id_from_entry(entry)


def desc_loc_from_entry(entry: dict) -> tuple[str, str]:
	return loc_id_from_entry(entry, desc=True)


def rarity_loc_from_rarity(rarity: int) -> tuple[str, str]:
	from core.format.mapping_loc import loc_id_for_key
	from core.game_logic.enums import Rarity

	loc_id = loc_id_for_key("General", Rarity(rarity).name)
	return loc_id, "General"


def ascension_loc_from_level(level) -> tuple[str, str]:
	from core.format.mapping_loc import loc_id_for_key
	from core.game_logic.enums import AscensionLevel

	if level == AscensionLevel.None_:
		return "", "General"
	loc_id = loc_id_for_key("General", level.name)
	return loc_id, "General"


def load_shared_loc_ids() -> dict[str, dict[str, str]]:
	from core.format.localizer_base import load_shared_loc_ids as _load_shared_loc_ids

	return _load_shared_loc_ids()


def loc_id_for_key(table: str, key: str) -> str:
	return core_loc_id_for_key(table, key)


def bracketed_title(
	rarity_loc_id: str,
	rarity_table: str,
	name_loc_id: str,
	name_table: str,
	*,
	language: str | None = None,
) -> str:
	rarity = get_localized(rarity_loc_id, table=rarity_table, language=language)
	name = get_localized(name_loc_id, table=name_table, language=language)
	return f"[{rarity}] {name}"


class LocalizationManager(QObject):
	def __init__(self, parent=None) -> None:
		super().__init__(parent)

	@Slot(str, str, str, "QVariantList", result=str)
	def get_string(
		self,
		loc_id: str,
		language: str,
		table: str = "General",
		args: list | None = None,
	) -> str:
		if args is None:
			args = []
		return get_localized(
			loc_id,
			table=table or "General",
			language=resolve_language(language or None),
			args=args,
		)

	@Slot(result=bool)
	def clear_cache(self) -> bool:
		clear_localization_cache()
		return True


def register_loc_manager(engine) -> LocalizationManager:
	instance = LocalizationManager(parent=engine)
	engine.rootContext().setContextProperty("LocManager", instance)
	return instance
