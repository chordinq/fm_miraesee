from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerEggModel
from controllers.common.timer_bar_bridge import TimerBarBridge
from ui.utils.localizer import bracketed_title, rarity_loc_from_rarity

_EGG_NAME_LOC_ID = "1084108339605504"
_EGG_NAME_LOC_TABLE = "Stats"


class EggModelBridge(QObject):

	changed = Signal()

	def __init__(
		self,
		egg: PlayerEggModel,
		player: PlayerModel,
		parent: QObject | None = None,
		language: str = "en",
	) -> None:
		super().__init__(parent)
		self._egg = egg
		self._player = player
		self._ui_language = language
		self._rarity: int = egg.rarity.value
		self._rarity_loc_id, self._rarity_loc_table = rarity_loc_from_rarity(self._rarity)
		self._title_text = self._build_title_text()
		self._timer_bar = TimerBarBridge(parent=self)
		self._timer_bar.displayChanged.connect(self.changed.emit)
		self._sync_timer()

	def _build_title_text(self) -> str:
		return bracketed_title(
			self._rarity_loc_id,
			self._rarity_loc_table,
			_EGG_NAME_LOC_ID,
			_EGG_NAME_LOC_TABLE,
			language=self._ui_language,
		)

	def _sync_timer(self) -> None:
		egg = self._egg
		if (
			egg.is_equipped
			and egg.hatch_timer_model is not None
			and egg.hatch_timer_model.end_time > egg.hatch_timer_model.start_time
		):
			self._timer_bar.bind(
				egg.hatch_timer_model,
				self._player,
				language=self._ui_language,
			)
		else:
			self._timer_bar.clear()

	def set_ui_language(self, language: str) -> None:
		if language == self._ui_language:
			return
		self._ui_language = language
		self._title_text = self._build_title_text()
		self._timer_bar.set_ui_language(language)
		self.changed.emit()

	def sync(self) -> None:
		self._title_text = self._build_title_text()
		self._sync_timer()
		self.changed.emit()

	def sync_quiet(self) -> None:
		self._sync_timer()

	@Property(int, notify=changed)
	def rarity(self) -> int:
		return self._rarity

	@Property(str, notify=changed)
	def rarityLocId(self) -> str:
		return self._rarity_loc_id

	@Property(str, notify=changed)
	def rarityLocTable(self) -> str:
		return self._rarity_loc_table

	@Property(str, notify=changed)
	def titleText(self) -> str:
		return self._title_text

	@Property(bool, notify=changed)
	def isEquipped(self) -> bool:
		return self._egg.is_equipped

	@Property(int, notify=changed)
	def equipSlot(self) -> int:
		return self._egg.equip_slot

	@Property(str, notify=changed)
	def guid(self) -> str:
		return self._egg.guid

	@Property(str, notify=changed)
	def seedText(self) -> str:
		return f"{self._egg.random_seed:#018x}"

	@Property(QObject, constant=True)
	def timerBridge(self) -> TimerBarBridge:
		return self._timer_bar
