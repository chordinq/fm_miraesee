from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtCore import QObject, Signal, Slot

from core.game_logic.player.player_model import PlayerModel
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def _apply_main_battle_progress(player: PlayerModel) -> None:
	player.main_battle_progress = SimpleNamespace(
		difficulty_idx=0,
		age_idx=99,
		battle_idx=0,
	)


class DumpLoadWorker(QObject):
	finished = Signal(object, str)

	@Slot(str)
	def parse(self, text: str) -> None:
		try:
			player = dump_snapshot_to_player_model(parse_dump_text(text))
			_apply_main_battle_progress(player)
			player.player_power_model.update_power(player, publish_update=True)
			self.finished.emit(player, "")
		except Exception as exc:
			self.finished.emit(None, str(exc))
