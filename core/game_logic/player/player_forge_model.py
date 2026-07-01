from __future__ import annotations
from typing import TYPE_CHECKING, Any
from ..enums import AscendableType, SecondaryStatType, StatType
from ..config.shared_game_config import AUTO_FORGE_HAMMER_UNLOCK_SEGMENTS
from ..unlock_extensions import is_unlocked
from ..stats.stat_helper import StatHelper
from ..stats.stat_target import ForgeStatTarget
from ...random_pcg import RandomPCG
from core.metaplaymath.config_values import config_f64_raw
from core.metaplaymath.f64 import f64_add_raw, f64_from_raw, f64_less_than_raw
from .ascension_model import AscensionModel
from .player_item_model import PlayerItemModel

if TYPE_CHECKING:
	from ..config.shared_game_config import SharedGameConfig
	from .player_model import PlayerModel


class PlayerForgeModel:
	def __init__(self, player: PlayerModel | None = None) -> None:
		self.pending_items: list[PlayerItemModel] = []
		self.forge_seed: int = 0
		self.forge_level: int = 0
		self.forge_upgrade_timer = None
		self.auto_forge_keep_ages: list[int] = []
		self.selected_auto_forge_hammer_count: int = 1
		self.forge_count: int = 0
		self.highest_age_of_crafted_item: int = 0
		self.current_forge_tier_level: int = 0
		self.passive_filter: list[SecondaryStatType] = []
		self.ascension_model = AscensionModel(AscendableType.Forge)
		self.is_auto_forge_active: bool = False
		self.items_marked_for_selling: set[str] = set()
		self.is_keep_auto_forge_active: bool = False

		if player is not None:
			self.add_keep_ages(player)

	def add_keep_ages(self, player: PlayerModel) -> None:
		max_age = int(player.game_config.base_config.get("MaxAge", 9))
		self.auto_forge_keep_ages = list(range(max_age + 1))

	def get_auto_forge_unlock_count_from_progress(self, player: PlayerModel) -> int:
		return sum(
			1
			for segment_id in AUTO_FORGE_HAMMER_UNLOCK_SEGMENTS
			if is_unlocked(segment_id, player)
		)

	def get_possible_auto_forge_hammer_count(self, player: PlayerModel) -> int:
		from ..stats.stat_helper import StatHelper

		unlock_count = self.get_auto_forge_unlock_count_from_progress(player)
		target = ForgeStatTarget()
		value = StatHelper.calculate_value(
			player,
			StatType.MaxCount,
			target,
			float(unlock_count),
		)
		return int(value)

	def try_get_current_forge_item(self) -> tuple[bool, PlayerItemModel | None]:
		for item in self.pending_items:
			if item.guid not in self.items_marked_for_selling:
				return True, item
		return False, None

	def forge_tiers_maxed(self, player: PlayerModel) -> bool:
		if self.forge_levels_maxed(player):
			return True
		game_config = player.game_config
		next_level = self.forge_level + 1
		tier_row = game_config.forge_upgrade_library.get(next_level)
		if tier_row is None:
			return True
		return self.current_forge_tier_level >= int(tier_row.get("Tiers", 0))

	def forge_levels_maxed(self, player: PlayerModel) -> bool:
		from ..config.shared_game_config import max_forge_level

		return self.forge_level >= max_forge_level(player.game_config)

	def forge_ascensions_maxed(self, player: PlayerModel) -> bool:
		return self.ascension_model.is_maxed(player.game_config)

	def forge_completely_maxed(self, player: PlayerModel) -> bool:
		return self.forge_levels_maxed(player) and self.forge_ascensions_maxed(player)

	def is_filter_unlocked(self, player: PlayerModel) -> bool:
		if forge_ascension_level(player) >= 1:
			return True

		game_config = player.game_config
		drop_row = game_config.item_age_drop_chances_library.get(self.forge_level)
		if drop_row is None:
			raise ValueError(f"No ItemAgeDropChanceInfo for forge level {self.forge_level}")

		chances = get_forge_drop_chances(drop_row)
		highest_age_with_chance = 0
		last_positive = 0
		for index, chance in enumerate(chances):
			if chance > 0:
				last_positive = index
			highest_age_with_chance = last_positive

		library = game_config.secondary_stat_item_unlock_library
		current_row = library.get(highest_age_with_chance)
		if current_row is None:
			raise ValueError(
				f"No SecondaryStatItemUnlockLibrary entry for age {highest_age_with_chance}"
			)

		current_stats = int(current_row.get("NumberOfSecondStats", 0))
		if current_stats <= 0 or highest_age_with_chance <= 0:
			return False

		prev_row = library.get(highest_age_with_chance - 1)
		if prev_row is None:
			raise ValueError(
				f"No SecondaryStatItemUnlockLibrary entry for age {highest_age_with_chance - 1}"
			)
		return int(prev_row.get("NumberOfSecondStats", 0)) > 0

	def should_auto_sell_item(self, item: PlayerItemModel) -> bool:
		return not self.keep_item_from_auto_sell(item)

	def keep_item_from_auto_sell(self, item: PlayerItemModel) -> bool:
		age = int(item.item_id.Age)
		if age not in self.auto_forge_keep_ages:
			return False
		if not self.passive_filter:
			return True
		return _filter_contains_item(self.passive_filter, item)

	def has_space_to_keep_auto_forging(self, player: PlayerModel) -> bool:
		kept = sum(
			1
			for item in self.pending_items
			if item.guid not in self.items_marked_for_selling
		)
		return kept < self.get_possible_auto_forge_hammer_count(player)

	def ascend(self, player: PlayerModel) -> None:
		self.pending_items.clear()
		self.auto_forge_keep_ages.clear()
		self.add_keep_ages(player)
		self.passive_filter.clear()
		self.forge_level = 0
		self.forge_upgrade_timer = None
		self.selected_auto_forge_hammer_count = 0
		self.highest_age_of_crafted_item = 0
		self.ascension_model.ascend()


def forge_ascension_level(player: PlayerModel) -> int:
	return player.player_forge_model.ascension_model.current_level


def _filter_contains_item(
	passive_filter: list[SecondaryStatType],
	item: PlayerItemModel,
) -> bool:
	item_types = set(item.secondary_stats.interpolated_stat_values)
	for stat_type in item_types:
		if stat_type in passive_filter:
			return True
	return False


def get_forge_tier_upgrade_cost(player: PlayerModel) -> int:
	"""IL: ForgeExtensions.GetForgeTierUpgradeCost."""
	forge = player.player_forge_model
	if forge.forge_tiers_maxed(player):
		return 0
	if forge.forge_levels_maxed(player):
		return 0

	upgrade_row = player.game_config.forge_upgrade_library.get(forge.forge_level + 1)
	if upgrade_row is None:
		raise ValueError(
			f"No ForgeUpgradeLibrary entry for level {forge.forge_level + 1}"
		)

	tiers = int(upgrade_row.get("Tiers", 0))
	cost = int(upgrade_row.get("Cost", 0))
	base_cost = cost // tiers if tiers != 0 else 0
	value = StatHelper.calculate_value(
		player,
		StatType.Cost,
		ForgeStatTarget(),
		base_cost,
	)
	return round(value)


_AGE_FIELD_NAMES = tuple(f"Age{i}" for i in range(10))


def get_forge_drop_chances(drop_row: dict[str, Any]) -> list[float]:
	"""Display path — F64 semantic doubles."""
	return [f64_from_raw(raw) for raw in get_forge_drop_chances_f64_raw(drop_row)]


def get_forge_drop_chances_f64_raw(drop_row: dict[str, Any]) -> list[int]:
	"""IL: ItemAgeDropChanceInfo.GetForgeDropChances — Age0..Age9 as F64.Raw."""
	return [config_f64_raw(drop_row[name]) for name in _AGE_FIELD_NAMES]


def roll_age(player: PlayerModel, rng: RandomPCG) -> int:
	"""IL: ForgeAction.RollAge — cumulative Age0..Age9 vs NextF64 (F64 compare)."""
	forge = player.player_forge_model
	game_config = player.game_config
	forge_level = forge.forge_level
	drop_row = game_config.item_age_drop_chances_library.get(forge_level)
	if drop_row is None:
		raise ValueError(f"No ItemAgeDropChanceInfo for forge level {forge_level}")

	chances = get_forge_drop_chances_f64_raw(drop_row)
	if not chances:
		return 0

	roll_raw = rng.next_f64_raw()
	accumulated = 0
	for index, chance_raw in enumerate(chances):
		accumulated = f64_add_raw(accumulated, chance_raw)
		if f64_less_than_raw(roll_raw, accumulated):
			return index
	return 0
