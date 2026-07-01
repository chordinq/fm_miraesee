from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from ..stats import StatContribution, StatContributions
from ..stats.stat_helper import StatHelper

if TYPE_CHECKING:
	from .player_model import PlayerModel


@dataclass(frozen=True)
class SetId:
	"""IL: Game.Logic.SetId — BaseSetId + ascension Level."""

	base_set_id: str
	level: int = 0


@dataclass
class SetBonusConfig:
	"""IL: Game.Logic.SetBonusConfig."""

	required_pieces: int
	bonus_stats: StatContributions
	stats_level_increment: float = 0.0


class PlayerSetsModel:
	"""IL: Game.Logic.PlayerSetsModel — ActivePiecesPerSetId at +0x10."""

	def __init__(self) -> None:
		self.active_pieces_per_set_id: dict[SetId, list[Any]] = {}

	def get_set_equipped_pieces_count(self, set_id: SetId) -> int:
		"""IL: PlayerSetsModel.GetSetEquippedPiecesCount."""
		pieces = self.active_pieces_per_set_id.get(set_id)
		if pieces is None:
			return 0
		return len(pieces)

	def all_active_set_bonus_tiers(
		self,
		game_config: Any,
	) -> list[SetBonusConfig]:
		"""IL: PlayerSetsModel.AllActiveSetBonusTiers."""
		result: list[SetBonusConfig] = []
		for set_id, pieces in self.active_pieces_per_set_id.items():
			if not pieces:
				continue
			result.extend(
				get_resolved_active_set_bonus_tiers(
					set_id,
					len(pieces),
					game_config,
				)
			)
		return result


# ── SetsExtensions ────────────────────────────────────────────────────────────


def _scale_tier_stats(
	tier: dict,
	ascension_bonus: float,
) -> list[StatContribution]:
	"""IL: SetsExtensions — value + bonus (FD6 add)."""
	from core.metaplaymath.fd6 import fd6_add_raw, fd6_from_double, fd6_to_double

	scaled: list[StatContribution] = []
	bonus_raw = fd6_from_double(ascension_bonus)
	for row in tier.get("BonusStats", {}).get("Stats", []):
		contribution = StatHelper.parse_stat_contribution_row(row)
		value = fd6_to_double(fd6_add_raw(contribution.raw, bonus_raw))
		scaled.append(StatContribution(contribution.node, value))
	return scaled


def _build_set_bonus_config(
	tier: dict,
	set_id: SetId,
) -> SetBonusConfig:
	increment = float(tier.get("StatsLevelIncrement", 0.0))
	ascension_bonus = increment * set_id.level
	return SetBonusConfig(
		required_pieces=int(tier.get("RequiredPieces", 0)),
		bonus_stats=StatContributions(stats=_scale_tier_stats(tier, ascension_bonus)),
		stats_level_increment=increment,
	)


def get_resolved_active_set_bonus_tiers(
	set_id: SetId,
	count_equipped: int,
	game_config: Any,
) -> list[SetBonusConfig]:
	"""IL: SetsExtensions.GetResolvedActiveSetBonusTiers."""
	sets_library = getattr(game_config, "sets_library", None)
	if sets_library is None:
		raise ValueError("game_config.sets_library is required")

	set_config = sets_library.get(set_id.base_set_id)
	if set_config is None:
		return []

	result: list[SetBonusConfig] = []
	for tier in set_config.get("BonusTiers", []):
		if count_equipped < int(tier.get("RequiredPieces", 0)):
			continue
		result.append(_build_set_bonus_config(tier, set_id))
	return result


def get_resolved_all_set_bonus_tiers(
	set_id: SetId,
	game_config: Any,
) -> list[SetBonusConfig]:
	"""IL: SetsExtensions.GetResolvedAllSetBonusTiers — all tiers, no piece-count filter."""
	sets_library = getattr(game_config, "sets_library", None)
	if sets_library is None:
		raise ValueError("game_config.sets_library is required")

	set_config = sets_library.get(set_id.base_set_id)
	if set_config is None:
		return []

	return [
		_build_set_bonus_config(tier, set_id)
		for tier in set_config.get("BonusTiers", [])
	]


def get_min_tier_bonus_piece_count(
	base_set_id: str,
	game_config: Any,
) -> int:
	"""IL: SetsExtensions.GetMinTierBonusPieceCount — min RequiredPieces across tiers."""
	sets_library = getattr(game_config, "sets_library", None)
	if sets_library is None:
		raise ValueError("game_config.sets_library is required")

	set_config = sets_library.get(base_set_id)
	if set_config is None:
		return 0

	required_counts = [
		int(tier.get("RequiredPieces", 0))
		for tier in set_config.get("BonusTiers", [])
	]
	if not required_counts:
		return 0
	return min(required_counts)


def active_set_bonus_tiers(
	player: PlayerModel,
	set_id: SetId,
) -> list[SetBonusConfig]:
	"""IL: SetsExtensions.ActiveSetBonusTiers(PlayerModel, SetId)."""
	count = player.sets_model.get_set_equipped_pieces_count(set_id)
	return get_resolved_active_set_bonus_tiers(
		set_id,
		count,
		player.game_config,
	)


def all_active_set_bonus_tiers(player: PlayerModel) -> list[SetBonusConfig]:
	"""IL: SetsExtensions.AllActiveSetBonusTiers(PlayerModel)."""
	return player.sets_model.all_active_set_bonus_tiers(player.game_config)
