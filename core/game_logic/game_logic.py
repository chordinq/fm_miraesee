"""
GameLogic entry point — player actions for offline simulation.
"""
from __future__ import annotations

from .actions import (
	ActionResult,
	AscendAction,
	EggSummonFinalizedAction,
	EquipItemAction,
	ForgeAction,
	ForgeGemSkipAction,
	ForgeTierUpgradeAction,
	ForgeUpgradeClaimAction,
	ForgeUpgradeStartAction,
	MetaActionResult,
	MountEquipAction,
	MountSummonFinalizedAction,
	MountUnEquipAction,
	PetEggHatchClaimAction,
	PetEggHatchFinalizedAction,
	PetEggHatchGemSkipAction,
	PetEggHatchStartAction,
	PetEquipAction,
	PetMergeAction,
	PetUnEquipAction,
	SellItemAction,
	SkillSummonFinalizedAction,
	SummonedEggInfo,
	SummonedMountsInfo,
	SummonedSkillInfo,
	SkillUpgradeAction,
	SkillsQuickUpgradeAction,
	SkillEquipAction,
	SkillUnEquipAction,
	TechTreeNodeUpgradeClaimAction,
	TechTreeNodeUpgradeGemSkipAction,
	TechTreeNodeUpgradeStartAction,
)
from .enums import AscendableType, TechTreeType
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
		"""IL: SkillSummonFinalizedAction."""
		action = SkillSummonFinalizedAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def skills_quick_upgrade(
		self,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list]:
		"""IL: SkillsQuickUpgradeAction."""
		action = SkillsQuickUpgradeAction()
		result = action.execute(self._player, commit=commit)
		return result, action.upgraded_skills

	def skills_quick_equip(
		self,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: QuickEquipSkillActionUiView.QuickEquip."""
		from .actions.skill.skills_quick_equip import quick_equip_skills

		return quick_equip_skills(self._player, commit=commit)

	def skill_equip(
		self,
		combat_skill,
		slot_id: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: SkillEquipAction."""
		action = SkillEquipAction(combat_skill, slot_id)
		return action.execute(self._player, commit=commit)

	def skill_unequip(
		self,
		combat_skill,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: SkillUnEquipAction."""
		action = SkillUnEquipAction(combat_skill)
		return action.execute(self._player, commit=commit)

	def equip_item(
		self,
		item_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: EquipItemAction."""
		action = EquipItemAction(item_guid)
		return action.execute(self._player, commit=commit)

	def sell_item(
		self,
		item_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: SellItemAction."""
		action = SellItemAction(item_guid)
		return action.execute(self._player, commit=commit)

	def forge_upgrade_start(
		self,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: ForgeUpgradeStartAction."""
		action = ForgeUpgradeStartAction()
		return action.execute(self._player, commit=commit)

	def forge_upgrade_claim(
		self,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: ForgeUpgradeClaimAction."""
		action = ForgeUpgradeClaimAction()
		return action.execute(self._player, commit=commit)

	def forge_tier_upgrade(
		self,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: ForgeTierUpgradeAction."""
		action = ForgeTierUpgradeAction()
		return action.execute(self._player, commit=commit)

	def forge_gem_skip(
		self,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: ForgeGemSkipAction."""
		action = ForgeGemSkipAction()
		return action.execute(self._player, commit=commit)

	def egg_summon(
		self,
		count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[SummonedEggInfo]]:
		"""IL: EggSummonFinalizedAction."""
		action = EggSummonFinalizedAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def mount_summon(
		self,
		count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[SummonedMountsInfo]]:
		"""IL: MountSummonFinalizedAction."""
		action = MountSummonFinalizedAction(count)
		result = action.execute(self._player, commit=commit)
		return result, action.summoned

	def mount_equip(
		self,
		mount_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: MountEquipAction."""
		action = MountEquipAction(mount_guid)
		return action.execute(self._player, commit=commit)

	def mount_unequip(
		self,
		mount_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: MountUnEquipAction."""
		action = MountUnEquipAction(mount_guid)
		return action.execute(self._player, commit=commit)

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
		forge_count: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, list[PlayerItemModel]]:
		"""IL: ForgeAction."""
		action = ForgeAction(forge_count)
		result = action.execute(self._player, commit=commit)
		return result, action.forged

	def ascend(
		self,
		ascendable_type: AscendableType,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: AscendAction."""
		action = AscendAction(ascendable_type)
		return action.execute(self._player, commit=commit)

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

	def pet_equip(
		self,
		pet_guid: str,
		slot_id: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetEquipAction."""
		action = PetEquipAction(pet_guid, slot_id)
		return action.execute(self._player, commit=commit)

	def pet_unequip(
		self,
		pet_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetUnEquipAction."""
		action = PetUnEquipAction(pet_guid)
		return action.execute(self._player, commit=commit)

	def pet_merge(
		self,
		target_guid: str,
		pet_sources: list[str] | None = None,
		egg_sources: list[str] | None = None,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetMergeAction."""
		action = PetMergeAction(target_guid, pet_sources, egg_sources)
		return action.execute(self._player, commit=commit)

	def pet_egg_hatch_claim(
		self,
		egg_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetEggHatchClaimAction."""
		action = PetEggHatchClaimAction(egg_guid)
		return action.execute(self._player, commit=commit)

	def pet_egg_hatch_gem_skip(
		self,
		egg_guid: str,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: PetEggHatchGemSkipAction."""
		action = PetEggHatchGemSkipAction(egg_guid)
		return action.execute(self._player, commit=commit)

	def pet_egg_hatch_complete(
		self,
		egg_guid: str,
		slot_index: int,
		*,
		commit: bool = True,
	) -> tuple[MetaActionResult, HatchedPetInfo | None]:
		"""Offline sim: Start → timer skip → Claim → Finalize (no gem cost)."""
		result = self.pet_egg_hatch_start(egg_guid, slot_index, commit=commit)
		if result != ActionResult.Success:
			return result, None

		if commit:
			from .actions.pet.pet_egg_hatch_action import _find_egg_by_guid

			egg = _find_egg_by_guid(self._player.player_pet_collection_model.eggs, egg_guid)
			if egg is None:
				return ActionResult.DoesNotExist, None
			if egg.hatch_timer_model is not None:
				egg.hatch_timer_model.skip_to_end(self._player)

			claim_result = self.pet_egg_hatch_claim(egg_guid, commit=True)
			if claim_result != ActionResult.Success:
				return claim_result, None

		return self.pet_egg_hatch_finalize(egg_guid, commit=commit)

	def tech_tree_node_upgrade_start(
		self,
		tree_type: TechTreeType,
		node_id: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: TechTreeNodeUpgradeStartAction."""
		action = TechTreeNodeUpgradeStartAction(tree_type, node_id)
		return action.execute(self._player, commit=commit)

	def tech_tree_node_upgrade_gem_skip(
		self,
		tree_type: TechTreeType,
		node_id: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: TechTreeNodeUpgradeGemSkipAction."""
		action = TechTreeNodeUpgradeGemSkipAction(tree_type, node_id)
		return action.execute(self._player, commit=commit)

	def tech_tree_node_upgrade_claim(
		self,
		tree_type: TechTreeType,
		node_id: int,
		*,
		commit: bool = True,
	) -> MetaActionResult:
		"""IL: TechTreeNodeUpgradeClaimAction."""
		action = TechTreeNodeUpgradeClaimAction(tree_type, node_id)
		return action.execute(self._player, commit=commit)
