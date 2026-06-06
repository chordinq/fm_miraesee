"""
GameLogic entry point — player actions for offline simulation.
"""
from __future__ import annotations

from .actions import (
	EggSummonAction,
	ForgeAction,
	MetaActionResult,
	MountSummonAction,
	PetEggHatchFinalizedAction,
	PetEggHatchStartAction,
	SkillSummonAction,
	SummonedEggInfo,
	SummonedMountsInfo,
	SummonedSkillInfo,
)
from .player.player_item_model import PlayerItemModel
from .player.player_pet_collection_model import HatchedPetInfo
from .player.player_model import PlayerModel


class GameLogic:
	def __init__(self, player: PlayerModel) -> None:
		self._player = player

	@property
	def player(self) -> PlayerModel:
		return self._player

	def skill_summon(
		self,
		count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[SummonedSkillInfo]]:
		"""IL: SkillSummonAction + SkillSummonFinalizedAction (merged)."""
		action = SkillSummonAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def egg_summon(
		self,
		count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[SummonedEggInfo]]:
		"""IL: EggSummonAction + EggSummonFinalizedAction (merged)."""
		action = EggSummonAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def mount_summon(
		self,
		count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[SummonedMountsInfo]]:
		"""IL: MountSummonAction + MountSummonFinalizedAction (merged)."""
		action = MountSummonAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def pet_egg_hatch_start(
		self,
		egg_guid: str,
		slot_index: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetEggHatchStartAction."""
		action = PetEggHatchStartAction(egg_guid, slot_index)
		return action.execute(self._player, commit=commit)

	def forge(
		self,
		hammer_count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[PlayerItemModel]]:
		"""IL: ForgeAction."""
		action = ForgeAction(hammer_count)
		result = action.execute(self._player, commit=commit)
		return result, action.forged

	def pet_egg_hatch_finalize(
		self,
		egg_guid: str,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, HatchedPetInfo | None]:
		"""IL: PetEggHatchFinalizedAction."""
		action = PetEggHatchFinalizedAction(egg_guid)
		result = action.execute(self._player, commit=commit)
		return result, action.hatched
