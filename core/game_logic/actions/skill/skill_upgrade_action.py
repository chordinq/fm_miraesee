from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ...enums import CombatSkill
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from ...player.player_skill_collection_model import PlayerSkillModel
from ...config.shared_game_config import can_be_upgraded_skill

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel

_OFFLINE_CLIENT_LISTENER: Any = object()


def apply_skill_upgrade(
	skill_model: PlayerSkillModel,
	upgrade_config: dict,
	client_listener: Any = _OFFLINE_CLIENT_LISTENER,
) -> None:
	"""IL: SkillUpgradeAction commit body / SkillsQuickUpgradeAction inner loop."""
	shard_cost = int(upgrade_config["Shards"])
	skill_model.spend_shards(shard_cost, client_listener)
	skill_model.level = int(upgrade_config["Level"])


class SkillUpgradeAction(PlayerAction):
	action_code = ActionCodes.SkillUpgrade

	def __init__(self, skill_to_upgrade: CombatSkill) -> None:
		super().__init__()
		self.skill_to_upgrade = skill_to_upgrade
		self.upgraded_skill: PlayerSkillModel | None = None

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		result, upgrade_config, skill_model = can_be_upgraded_skill(
			self.skill_to_upgrade,
			player,
		)
		if result != ActionResult.Success:
			return result
		if upgrade_config is None or skill_model is None:
			return ActionResult.UnknownError

		if not commit:
			return ActionResult.Success

		apply_skill_upgrade(skill_model, upgrade_config, _OFFLINE_CLIENT_LISTENER)
		self.upgraded_skill = skill_model
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
