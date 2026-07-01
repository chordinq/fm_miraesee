from __future__ import annotations

from typing import TYPE_CHECKING

from ...config.shared_game_config import _get_skill_rarity, get_unlocked_skill_slot_count
from ..action_result import ActionResult, MetaActionResult
from .skill_equip_action import SkillEquipAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


def quick_equip_skills(player: PlayerModel, *, commit: bool = True) -> MetaActionResult:
	"""IL: QuickEquipSkillActionUiView.QuickEquip — loops SkillEquipAction per slot."""
	collection = player.player_skill_collection_model
	skills = collection.player_skills
	if len(skills) == 0:
		return ActionResult.Success

	unlocked_slot_count = get_unlocked_skill_slot_count(player)
	if unlocked_slot_count <= 0:
		return ActionResult.Success

	game_config = player.game_config
	sorted_skills = sorted(
		skills.values(),
		key=lambda skill: (
			-_get_skill_rarity(game_config, skill.type).value,
			-skill.level,
			skill.type.value,
		),
	)

	for slot_id in range(unlocked_slot_count):
		if slot_id >= len(sorted_skills):
			continue

		skill = sorted_skills[slot_id]
		if skill.is_equipped and skill.equip_slot == slot_id:
			continue

		action = SkillEquipAction(skill.type, slot_id)
		result = action.execute(player, commit=commit)
		if result not in (ActionResult.Success, ActionResult.AlreadyEquipped):
			return result

	return ActionResult.Success
