from __future__ import annotations

from typing import TYPE_CHECKING

from ...enums import CurrencyType
from ...player.player_item_model import get_sell_value
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


class SellItemAction(PlayerAction):
	action_code = ActionCodes.Sell

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

		equipped = player.player_equipment_model.get_equipped_item(item.item_id.Type)
		if equipped is not None:
			equipped.is_new = False

		if item in pending_items:
			pending_items.remove(item)

		sell_value = get_sell_value(player, item)
		player.player_currency_model.add(CurrencyType.Coins, sell_value)
		return ActionResult.Success
