from __future__ import annotations

from typing import TYPE_CHECKING

from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...player.player_mount_collection_model import PlayerMountModel


def _find_mount_by_guid(
	mounts: list[PlayerMountModel],
	mount_guid: str,
) -> PlayerMountModel | None:
	for mount in mounts:
		if mount.guid == mount_guid:
			return mount
	return None


def _find_equipped_mount(mounts: list[PlayerMountModel]) -> PlayerMountModel | None:
	for mount in mounts:
		if mount.is_equipped:
			return mount
	return None


class MountEquipAction(PlayerAction):
	action_code = ActionCodes.MountEquip

	def __init__(self, mount_to_equip: str) -> None:
		super().__init__()
		self.mount_to_equip = mount_to_equip

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		collection = player.player_mount_collection_model
		mount = _find_mount_by_guid(collection.player_mount_models, self.mount_to_equip)
		if mount is None:
			return ActionResult.DoesNotExist

		if mount.is_equipped:
			return ActionResult.AlreadyEquipped

		if not commit:
			return ActionResult.Success

		previously_equipped = _find_equipped_mount(collection.player_mount_models)
		if previously_equipped is not None:
			previously_equipped.is_equipped = False

		mount.is_equipped = True
		player.player_power_model.update_power(player, publish_update=True)
		return ActionResult.Success
