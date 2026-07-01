"""IL: Game.Logic.UnlockExtensions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from .config.shared_game_config import is_age_gate_unlocked
from .config.summon_config import SummonConfig
from .enums import AscendableType
from .player.summon_model import is_summon_level_maxed

if TYPE_CHECKING:
	from .player.player_model import PlayerModel

# IL: PlayerSegment property evaluators for ascension segments (PlayerPropertyId*).
_ASCENSION_SEGMENT_CHECKS: dict[str, Callable[[PlayerModel], bool]] = {
	"ForgeAscension": lambda player: player.player_forge_model.forge_levels_maxed(
		player
	),
	"MountsAscension": lambda player: is_summon_level_maxed(
		player.player_mount_collection_model.summon_model,
		SummonConfig(AscendableType.Mounts),
	),
	"PetsAscension": lambda player: is_summon_level_maxed(
		player.player_pet_collection_model.summon_model,
		SummonConfig(AscendableType.Pets),
	),
	"SkillsAscension": lambda player: is_summon_level_maxed(
		player.player_skill_collection_model.summon_model,
		SummonConfig(AscendableType.Skills),
	),
}

# IL: UnlockExtensions cctor static dicts — segment-specific overrides only.
_DICT1_SEGMENT_CHECKS: dict[str, Callable[[PlayerModel], bool]] = {}
_DICT2_SEGMENT_CHECKS: dict[str, Callable[[PlayerModel], bool]] = {}


def _config_unlocked(segment_id: str, player: PlayerModel) -> bool:
	"""IL: TryGetUnlockCondition delegate, default true when no row."""
	condition = player.game_config.unlock_conditions_library.get(segment_id)
	if condition is None:
		return True
	return is_age_gate_unlocked(condition, player)


def _dict1_unlocked(segment_id: str, player: PlayerModel) -> bool:
	"""IL: first static dict — default true when segment absent."""
	evaluator = _DICT1_SEGMENT_CHECKS.get(segment_id)
	if evaluator is None:
		return True
	return evaluator(player)


def _dict2_unlocked(segment_id: str, player: PlayerModel) -> bool:
	"""IL: second static dict — default false when segment absent."""
	evaluator = _DICT2_SEGMENT_CHECKS.get(segment_id)
	if evaluator is None:
		return False
	return evaluator(player)


def _player_segment_property_met(segment_id: str, player: PlayerModel) -> bool:
	"""IL: PlayerSegmentInfoBase.MatchesPlayer for known ascension segments."""
	evaluator = _ASCENSION_SEGMENT_CHECKS.get(segment_id)
	if evaluator is not None:
		return evaluator(player)
	if segment_id in player.game_config.player_segments_library:
		return True
	return True


def is_unlocked(segment_id: str, player: PlayerModel) -> bool:
	"""IL: UnlockExtensions.IsUnlocked — dict2 | (dict1 & config & segment)."""
	config_ok = _config_unlocked(segment_id, player)
	dict1_ok = _dict1_unlocked(segment_id, player)
	dict2_ok = _dict2_unlocked(segment_id, player)
	segment_ok = _player_segment_property_met(segment_id, player)
	if segment_id in player.game_config.player_segments_library:
		return dict2_ok or (dict1_ok and config_ok and segment_ok)
	return dict2_ok or (dict1_ok and config_ok)
