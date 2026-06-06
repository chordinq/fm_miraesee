from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
	from .player.player_model import PlayerModel

AUTO_FORGE_HAMMER_UNLOCK_SEGMENTS: tuple[str, ...] = ("Hammer_1", "Hammer_2")


def is_unlocked(segment_id: str, player: PlayerModel) -> bool:
	condition = player.game_config.unlock_conditions_library.get(segment_id)
	if condition is None:
		return False
	return is_age_gate_unlocked(condition, player)


def is_age_gate_unlocked(condition: dict[str, Any], player: PlayerModel) -> bool:
	progress = getattr(player, "main_battle_progress", None)
	if progress is None:
		return False
	difficulty = int(condition.get("DifficultyIdx", 0))
	age = int(condition.get("AgeIdx", 0))
	battle = int(condition.get("BattleIdx", 0))
	player_difficulty = int(getattr(progress, "difficulty_idx", 0))
	player_age = int(getattr(progress, "age_idx", 0))
	player_battle = int(getattr(progress, "battle_idx", 0))
	if player_difficulty != difficulty:
		return player_difficulty > difficulty
	if player_age != age:
		return player_age > age
	return player_battle >= battle
