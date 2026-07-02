from __future__ import annotations

from PySide6.QtCore import QObject, Property, Signal

from config import PETS_MAPPING
from core.format.format_item import format_secondary_stats
from core.format.localizer_base import selected_language
from core.format.stats_format import format_stat_node
from core.game_logic.config.shared_game_config import SharedGameConfig, get_unlocked_pet_slot_count
from core.game_logic.player.player_model import PlayerModel, get_total_stats
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
from core.metaplaymath.f64 import f64_from_raw
from ui.utils.localizer import bracketed_title, name_loc_from_entry, rarity_loc_from_rarity


def build_pet_stat_lines(
	player: PlayerModel,
	pet: PlayerPetModel,
	*,
	language: str | None = None,
) -> list[dict[str, object]]:
	"""IL: PetDetailsUiView.UpdateUi → SharedGameConfigExtensions.FormatPetStats."""
	lang = selected_language() if language is None else language
	game_config = player.game_config
	total_stats = get_total_stats(player)
	resolved = SharedGameConfig.get_resolved_pet_stats(
		game_config,
		pet.pet_id,
		pet.level,
		total_stats,
	)

	lines: list[dict[str, object]] = []
	for stat_node, raw_value in resolved.iter_stat_contributions_double():
		text = format_stat_node(
			stat_node,
			raw_value,
			show_multipliers_as_percentage=False,
			show_value_at_end=False,
			language=lang,
		)
		if text:
			lines.append({"text": text, "secondary": False})

	if pet.secondary_stats.interpolated_stat_values:
		for stat_type in pet.secondary_stats.interpolated_stat_values.keys():
			found, raw_value = pet.secondary_stats.try_get_stat_value(stat_type, game_config)
			if not found:
				continue
			text = format_secondary_stats(
				stat_type,
				raw_value,
				game_config,
				language=lang,
			)
			if not text:
				continue
			lines.append(
				{
					"text": text,
					"secondary": True,
					"rollT": f64_from_raw(
						pet.secondary_stats.interpolated_stat_values[stat_type]
					),
				}
			)

	return lines


class PetModelBridge(QObject):

	changed = Signal()

	def __init__(
		self,
		pet: PlayerPetModel,
		player: PlayerModel,
		parent: QObject | None = None,
	) -> None:
		super().__init__(parent)
		self._pet = pet
		self._player = player
		self._rebuild()

	def _build_title_text(self) -> str:
		return bracketed_title(
			self._rarity_loc_id,
			self._rarity_loc_table,
			self._name_loc_id,
			self._name_loc_table,
		)

	def _rebuild(self) -> None:
		pet = self._pet

		key = f"{pet.pet_id.rarity.value}_{pet.pet_id.id}"
		entry = PETS_MAPPING[key]

		self._guid = pet.guid
		self._index = pet.pet_id.id
		self._rarity = entry["Rarity"]
		self._pet_key = entry["Key"]
		self._name_loc_id, self._name_loc_table = name_loc_from_entry(entry)
		self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
		self._title_text = self._build_title_text()
		self._stat_lines: list[dict[str, object]] | None = None
		self._base_stat_lines: list[dict[str, object]] | None = None
		self._sub_stat_lines: list[dict[str, object]] | None = None

	def _ensure_stat_lines(self) -> None:
		if self._stat_lines is not None:
			return
		lines = build_pet_stat_lines(self._player, self._pet)
		self._stat_lines = lines
		self._base_stat_lines = [line for line in lines if not line["secondary"]]
		self._sub_stat_lines = [line for line in lines if line["secondary"]]

	def _clear_stat_cache(self) -> None:
		self._stat_lines = None
		self._base_stat_lines = None
		self._sub_stat_lines = None

	def invalidate_stat_cache(self) -> None:
		if self._stat_lines is None:
			return
		self._clear_stat_cache()
		self.changed.emit()

	def refresh_localized(self) -> None:
		self._title_text = self._build_title_text()
		self._clear_stat_cache()
		self.changed.emit()

	def sync(self) -> None:
		self._title_text = self._build_title_text()
		self._clear_stat_cache()
		self.changed.emit()

	def refresh(self) -> None:
		self.sync()

	@Property(str, notify=changed)
	def guid(self) -> str:
		return self._guid

	@Property(int, notify=changed)
	def index(self) -> int:
		return self._index

	@Property(int, notify=changed)
	def rarity(self) -> int:
		return self._rarity

	@Property(int, notify=changed)
	def level(self) -> int:
		return self._pet.level

	@Property(int, notify=changed)
	def equipSlot(self) -> int:
		return self._pet.equip_slot

	@Property(bool, notify=changed)
	def isEquipped(self) -> bool:
		return self._pet.is_equipped

	@Property(bool, notify=changed)
	def isLocked(self) -> bool:
		return self._pet.is_locked

	@Property(bool, notify=changed)
	def canEquip(self) -> bool:
		if self._pet.is_equipped:
			return True
		return get_unlocked_pet_slot_count(self._player) > 0

	@Property(str, notify=changed)
	def petKey(self) -> str:
		return self._pet_key

	@Property(str, notify=changed)
	def nameLocId(self) -> str:
		return self._name_loc_id

	@Property(str, notify=changed)
	def nameLocTable(self) -> str:
		return self._name_loc_table

	@Property(str, notify=changed)
	def rarityLocId(self) -> str:
		return self._rarity_loc_id

	@Property(str, notify=changed)
	def rarityLocTable(self) -> str:
		return self._rarity_loc_table

	@Property(str, notify=changed)
	def titleText(self) -> str:
		return self._title_text

	@Property("QVariantList", notify=changed)
	def statLines(self) -> list[dict[str, object]]:
		self._ensure_stat_lines()
		return self._stat_lines or []

	@Property("QVariantList", notify=changed)
	def baseStatLines(self) -> list[dict[str, object]]:
		self._ensure_stat_lines()
		return self._base_stat_lines or []

	@Property("QVariantList", notify=changed)
	def subStatLines(self) -> list[dict[str, object]]:
		self._ensure_stat_lines()
		return self._sub_stat_lines or []
