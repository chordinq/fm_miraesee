from __future__ import annotations

from typing import TYPE_CHECKING

from ...player.player_equipment_model import (
	get_default_weapon_item_id,
	item_id_equals,
)
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_item_model import PlayerItemModel
	from ...player.player_model import PlayerModel


def _find_pending_item(
	pending_items: list[PlayerItemModel],
	item_guid: str,
) -> PlayerItemModel | None:
	for item in pending_items:
		if item.guid == item_guid:
			return item
	return None


def _should_return_equipped_to_inventory(equipped_item_id) -> bool:
	try:
		default_weapon_id = get_default_weapon_item_id()
	except NotImplementedError:
		return True
	return not item_id_equals(equipped_item_id, default_weapon_id)


def _should_clear_is_new_on_equip(equipped_item_id) -> bool:
	if equipped_item_id is None:
		return True
	try:
		default_weapon_id = get_default_weapon_item_id()
	except NotImplementedError:
		return False
	return item_id_equals(equipped_item_id, default_weapon_id)


class EquipItemAction(PlayerAction):
	action_code = ActionCodes.Equip

	def __init__(self, item_guid: str) -> None:
		super().__init__()
		self.item_guid = item_guid

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		pending_items = player.player_forge_model.pending_items
		if not pending_items:
			return ActionResult.NoItems

		item = _find_pending_item(pending_items, self.item_guid)
		if item is None:
			return ActionResult.DoesNotExist

		if not commit:
			return ActionResult.Success

		item.is_newly_forged = False
		if item in pending_items:
			pending_items.remove(item)

		equipment = player.player_equipment_model
		equipped = equipment.get_equipped_item(item.item_id.Type)
		if equipped is None:
			item.is_new = False
		else:
			equipped_item_id = equipped.item_id
			if _should_return_equipped_to_inventory(equipped_item_id):
				pending_items.insert(0, equipped)
			if _should_clear_is_new_on_equip(equipped_item_id):
				item.is_new = False

		equipment.equip_item(player, item)
		return ActionResult.Success
