from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from ...player.player_skill_collection_model import PlayerSkillModel
from ...shared_game_config import can_be_upgraded
from .skill_upgrade_action import _OFFLINE_CLIENT_LISTENER, apply_skill_upgrade

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel

_MAX_UPGRADES_PER_SKILL = 100


class SkillsQuickUpgradeAction(PlayerAction):
	action_code = ActionCodes.SkillQuickUpgrade

	def __init__(self) -> None:
		super().__init__()
		self.upgraded_skills: list[PlayerSkillModel] = []

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_skill_collection_model
		skills = collection.player_skills

		if len(skills) == 0:
			return ActionResult.DoesNotExist

		can_upgrade_any = any(
			can_be_upgraded(skill, player)[0] == ActionResult.Success
			for skill in skills.values()
		)
		if not can_upgrade_any:
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		self.upgraded_skills = []
		for skill in skills.values():
			for _ in range(_MAX_UPGRADES_PER_SKILL):
				result, upgrade_config = can_be_upgraded(skill, player)
				if result != ActionResult.Success:
					break
				if upgrade_config is None:
					break
				apply_skill_upgrade(skill, upgrade_config, _OFFLINE_CLIENT_LISTENER)
				self.upgraded_skills.append(skill)

		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
