from __future__ import annotations
import math
from typing import TYPE_CHECKING, Any
from ...enums import CurrencyType, ItemAge, ItemType, SecondaryStatType, StatType
from ....random_pcg import RandomPCG
from ...item_age_drop import roll_age
from ...player.player_equipment_model import ItemId
from ...player.player_forge_model import forge_ascension_level
from ...player.player_item_model import PlayerItemModel
from ...stats.secondary_stat_helper import SecondaryStatHelper
from ...stats.stat_helper import StatHelper
from ...stats.stat_target import EquipmentStatTarget, ForgeStatTarget
from ..action_codes import ActionCodes
from ..action_result import ActionResult, MetaActionResult
from ..player_action import PlayerAction

if TYPE_CHECKING:
	from ...player.player_model import PlayerModel
	from ...shared_game_config import SharedGameConfig

_TUTORIAL_SANDALS = ItemId(ItemAge(1), ItemType.Shoes, 0)
_TUTORIAL_ITEMS_BY_FORGE_COUNT: dict[int, tuple[ItemId, int]] = {
	0: (ItemId(ItemAge(5), ItemType.Weapon, 0), 2),
	1: (ItemId(ItemAge(1), ItemType.Weapon, 0), 1),
}


class ForgeAction(PlayerAction):
	action_code = ActionCodes.Forge

	def __init__(self, hammer_count: int) -> None:
		super().__init__()
		self.hammer_count = hammer_count
		self.forged: list[PlayerItemModel] = []

	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		self.forged = []
		if self.hammer_count < 1:
			return ActionResult.DoesNotExist

		forge = player.player_forge_model
		game_config = player.game_config
		forge_cost = game_config.forge_config.forge_cost

		if self.hammer_count >= 2:
			max_auto = forge.get_possible_auto_forge_hammer_count(player)
			if self.hammer_count > max_auto:
				return ActionResult.NotEnoughResources

		hammers = player.player_currency_model.get(CurrencyType.Hammers)
		effective_hammers = min(self.hammer_count, hammers)
		if effective_hammers < 1:
			return ActionResult.NotEnoughResources

		total_cost = effective_hammers * forge_cost
		spend_ctx = player.player_currency_model.create_spend_context(
			CurrencyType.Hammers,
			total_cost,
		)
		if not spend_ctx.can_afford():
			return ActionResult.NotEnoughResources

		if not commit:
			return ActionResult.Success

		freebie_target = ForgeStatTarget()
		loop_count = effective_hammers
		bonus_forges = 0
		i = 0

		while i < loop_count:
			rng = RandomPCG.create_from_seed(forge.forge_seed)

			age = roll_age(player, rng)
			possible = _get_possible_items(game_config, age)
			item = _create_forge_item(player, possible, rng, age)
			if item is None:
				return ActionResult.DoesNotExist

			if i < self.hammer_count:
				if StatHelper.roll_stat(
					player,
					StatType.FreebieChance,
					freebie_target,
					rng,
				):
					bonus_forges += 1
					if loop_count == self.hammer_count:
						spend_ctx.free(forge_cost)
					else:
						loop_count = min(self.hammer_count, loop_count + 1)

			forge.forge_seed = (forge.forge_seed + 1) & 0xFFFFFFFFFFFFFFFF
			forge.forge_count += 1
			forge.highest_age_of_crafted_item = max(
				forge.highest_age_of_crafted_item,
				int(item.item_id.Age),
			)
			item.is_newly_forged = True
			forge.pending_items.insert(0, item)

			if forge.is_auto_forge_active and not forge.keep_item_from_auto_sell(item):
				forge.items_marked_for_selling.add(item.guid)

			equipment = player.player_equipment_model
			equipment.increment_hidden_item_level(player, item.item_id)

			type_pool = possible.get(item.item_id.Type, [])
			type_ids = [_row_item_id(row) for row in type_pool]
			equipment.add_or_reset_round_robin(type_ids, item.item_id)

			self.forged.append(item)
			i += 1

		spend_ctx.spend("Forge")
		return ActionResult.Success


def _get_possible_items(
	game_config: SharedGameConfig,
	age: int,
) -> dict[ItemType, list[dict[str, Any]]]:
	grouped: dict[ItemType, list[dict[str, Any]]] = {}
	for item_id, info in game_config.items.items():
		if int(item_id.Age) != age:
			continue
		grouped.setdefault(item_id.Type, []).append(info)
	return grouped


def _row_item_id(row: dict[str, Any]) -> ItemId:
	if "ItemId" in row:
		from ...shared_game_config import parse_item_id_from_row

		return parse_item_id_from_row(row)
	raise ValueError("equipment row missing ItemId")


def _create_forge_item(
	player: PlayerModel,
	possible: dict[ItemType, list[dict[str, Any]]],
	rng: RandomPCG,
	age: int,
) -> PlayerItemModel | None:
	forge = player.player_forge_model
	game_config = player.game_config

	tutorial = _TUTORIAL_ITEMS_BY_FORGE_COUNT.get(forge.forge_count)
	if tutorial is not None:
		item_id, level = tutorial
		return _create_specific_item(item_id, forge.forge_seed, level)
	if (
		forge.highest_age_of_crafted_item == 0
		and forge.forge_level > 0
		and forge.ascension_model.current_level < 1
	):
		return _create_specific_item(_TUTORIAL_SANDALS, forge.forge_seed, 0)

	return _create_random_item(player, possible, rng, age)


def _create_specific_item(item_id: ItemId, seed: int, level: int) -> PlayerItemModel:
	rng = RandomPCG.create_from_seed(seed)
	item = PlayerItemModel(rng.next_guid(), item_id, level)
	item.is_newly_forged = True
	return item


def _create_random_item(
	player: PlayerModel,
	possible: dict[ItemType, list[dict[str, Any]]],
	rng: RandomPCG,
	age: int,
) -> PlayerItemModel | None:
	if not possible:
		return None

	item_type = rng.choice(
		(t for t in sorted(possible.keys(), key=lambda t: int(t)))
	)
	pool = possible[item_type]
	if not pool:
		return None

	game_config = player.game_config
	equipment = player.player_equipment_model
	all_ids = [_row_item_id(row) for row in pool]
	equipment.try_reset_round_robin(all_ids, item_type, age)

	rolled = set(equipment.get_round_robin_list(item_type, age))
	candidates = [row for row in pool if _row_item_id(row).Idx not in rolled]
	if not candidates:
		candidates = pool

	guid = rng.next_guid()
	chosen_row = rng.choice(candidates)
	item_id = _row_item_id(chosen_row)
	item = PlayerItemModel(guid, item_id, 0)

	level = _roll_item_level(player, rng, age, item_type)
	item.level = level

	stat_count = _secondary_stat_count(player, age)
	excluded: list[SecondaryStatType] | None = None
	if item_id.Type == ItemType.Weapon:
		weapon_info = game_config.weapons.get(item_id)
		if weapon_info is not None:
			if weapon_info.get("IsRanged", False):
				excluded = [SecondaryStatType.MeleeDamageMulti]
			else:
				excluded = [SecondaryStatType.RangedDamageMulti]

	item.secondary_stats = SecondaryStatHelper.generate_secondary_stats(
		stat_count, rng, excluded
	)
	item.is_newly_forged = True
	return item


def _secondary_stat_count(player: PlayerModel, age: int) -> int:
	game_config = player.game_config
	ascension_level = forge_ascension_level(player)
	library = game_config.secondary_stat_item_unlock_library
	if ascension_level < 1:
		row = library.get(age)
	else:
		row = list(library.values())[-1] if library else None
	if row is None:
		return 0
	return int(row.get("NumberOfSecondStats", 0))


def _roll_item_level(
	player: PlayerModel,
	rng: RandomPCG,
	age: int,
	item_type: ItemType,
) -> int:
	game_config = player.game_config
	equipment = player.player_equipment_model
	bracket_key = equipment.get_hidden_level(item_type, age)
	bracket = game_config.item_level_brackets_library.get(bracket_key)
	if bracket is None:
		bracket = game_config.item_level_brackets_library.get(0, {})

	base_max = game_config.item_balancing_config.item_base_max_level
	target = EquipmentStatTarget(item_type)
	calculated = StatHelper.calculate_value(
		player,
		StatType.MaxLevel,
		target,
		base_max,
	)
	cap = int(bracket.get("UpperRange", 0))
	floored = int(math.floor(calculated))
	max_level = min(cap, floored)
	lower = int(bracket.get("LowerRange", 0))
	return rng.next_int_min_max(lower, max_level + 1)
