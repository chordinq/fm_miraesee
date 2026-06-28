from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction
from .mount_equip_action import _find_mount_by_guid

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel


class MountUnEquipAction(PlayerAction):
	action_code = ActionCodes.MountUnEquip

	def __init__(self, mount_to_unequip: str) -> None:
		super().__init__()
		self.mount_to_unequip = mount_to_unequip

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_mount_collection_model
		mount = _find_mount_by_guid(collection.player_mount_models, self.mount_to_unequip)
		if mount is None:
			return ActionResult.DoesNotExist

		if not mount.is_equipped:
			return ActionResult.NotEquipped

		if not commit:
			return ActionResult.Success

		mount.is_equipped = False
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
