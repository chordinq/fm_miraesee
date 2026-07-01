from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from ..enums import ItemType, SecondaryStatType, StatType
from ..config.shared_game_config import SharedGameConfig
from ..stats import StatNode, Stats
from ..stats.skill_stats import SkillStats
from ..stats.stat_calc import StatCalcContext
from ..stats.stat_helper import StatHelper
from ..stats.stat_target import StatTarget
from .player_currency_model import PlayerCurrencyModel
from .player_equipment_model import ItemId, ItemModel
from .player_equipment_model import PlayerEquipmentModel
from .player_forge_model import PlayerForgeModel
from .player_item_model import PlayerItemModel
from .player_mount_collection_model import PlayerMountCollectionModel
from .player_pet_collection_model import PlayerPetCollectionModel
from .player_power_model import PlayerPowerModel
from .player_sets_model import PlayerSetsModel
from .player_skill_collection_model import PlayerSkillCollectionModel
from .player_skin_collection_model import (
	PlayerSkinCollectionModel,
	get_resolved_stat_contributions,
)
from .player_techtree_model import PlayerTechTreeModel

if TYPE_CHECKING:
	from .player_mount_collection_model import PlayerMountModel
	from .player_skin_collection_model import PlayerSkinModel


class PlayerModel:
	def __init__(self, game_config: SharedGameConfig | Any | None = None) -> None:
		self._game_config = game_config
		self.player_currency_model = PlayerCurrencyModel()
		self.player_forge_model = PlayerForgeModel()
		self.player_equipment_model = PlayerEquipmentModel()
		self.player_skill_collection_model = PlayerSkillCollectionModel()
		self.player_power_model = PlayerPowerModel()
		self.player_techtree_model = PlayerTechTreeModel()
		self.player_pet_collection_model = PlayerPetCollectionModel()
		self.player_mount_collection_model = PlayerMountCollectionModel()
		self.player_skin_collection_model = PlayerSkinCollectionModel()
		self.sets_model = PlayerSetsModel()
		self._server_time_seconds: int = 0
		self._wall_clock_server_time: bool = False

	def get_server_time(self) -> int:
		"""IL: PlayerModel.get_ServerTime — sim clock, or wall clock after dump load."""
		if self._wall_clock_server_time:
			return int(time.time())
		return self._server_time_seconds

	def enable_wall_clock_server_time(self) -> None:
		self._wall_clock_server_time = True

	def advance_server_time(self, seconds: int) -> None:
		self._wall_clock_server_time = False
		self._server_time_seconds += seconds

	@property
	def game_config(self) -> Any:
		if self._game_config is not None:
			return self._game_config
		from ..stats.pet_stats import load_pet_stats_config

		return load_pet_stats_config()

	@property
	def is_ranged(self) -> bool:
		"""IL: PlayerModel.get_IsRanged."""
		from .player_item_model import is_ranged_weapon

		weapon = self.player_equipment_model.weapon
		if weapon is None:
			return False
		return is_ranged_weapon(weapon.item_id, self.game_config)


# ── PlayerModelItemExtensions ─────────────────────────────────────────────────


def get_total_stats(player: PlayerModel) -> Stats:
	power = player.player_power_model
	if power.stats is None:
		power.update_power(player, True)
	if power.stats is None:
		raise RuntimeError("PlayerPowerModel.stats unset after UpdatePower")
	return power.stats


def calculate_total_stats(player: PlayerModel) -> Stats:
	total_stats = Stats()
	total_stats.add_stat_contributions(get_base_stats(player))
	total_stats.add_stat_contributions(get_all_secondary_stats(player))
	total_stats.add_stat_contributions(get_ascension_stats(player))
	total_stats.add_stat_contributions(
		player.player_techtree_model.get_total_stats(player)
	)

	equipment_stats = Stats()
	for item in player.player_equipment_model.get_items().values():
		resolved = get_resolved_item_stats(player.game_config, item, total_stats)
		equipment_stats.add_stat_contributions(resolved)

	pet_stats = Stats()
	for pet in player.player_pet_collection_model.get_equipped_pets():
		resolved = SharedGameConfig.get_resolved_pet_stats(
			player.game_config,
			pet.pet_id,
			pet.level,
			total_stats,
		)
		_merge_into_stats(pet_stats, resolved)

	mount_stats = Stats()
	equipped_mount = _first_equipped_mount(player)
	if equipped_mount is not None:
		resolved = SharedGameConfig.get_resolved_mount_stats(
			player.game_config,
			equipped_mount.mount_id,
			equipped_mount.level,
			total_stats,
		)
		_merge_into_stats(mount_stats, resolved)

	skill_stats = Stats()
	for skill in player.player_skill_collection_model.player_skills.values():
		resolved = SharedGameConfig.get_resolved_passive_skill_stats(
			player.game_config,
			skill.type,
			skill.level,
			total_stats,
		)
		_merge_into_stats(skill_stats, resolved)

	skin_stats = Stats()
	for skin in player.player_skin_collection_model.get_equipped_skins().values():
		_add_skin_stat_contributions(skin_stats, skin, player)

	sets_stats = Stats()
	for bonus in player.sets_model.all_active_set_bonus_tiers(player.game_config):
		sets_stats.add_stat_contributions(bonus.bonus_stats)

	total_stats.add_stat_contributions(equipment_stats)
	total_stats.add_stat_contributions(pet_stats)
	total_stats.add_stat_contributions(mount_stats)
	total_stats.add_stat_contributions(skill_stats)
	total_stats.add_stat_contributions(skin_stats)
	total_stats.add_stat_contributions(sets_stats)
	return total_stats


def get_base_stats(player: PlayerModel) -> Stats:
	config = player.game_config
	balancing = config.item_balancing_config
	if balancing is None:
		raise ValueError("item_balancing_config is required for GetBaseStats")

	result = Stats()
	target = StatTarget.player()
	result.add_stat_contribution(
		StatHelper.new_additive_stat_node(StatType.Damage, target),
		balancing.player_base_damage,
	)
	result.add_stat_contribution(
		StatHelper.new_additive_stat_node(StatType.Health, target),
		balancing.player_base_health,
	)
	crit_node = StatHelper.new_multiplicative_node(
		StatType.CriticalDamage, target
	)
	result.add_secondary_stat_contribution(
		SecondaryStatType.CriticalMulti,
		balancing.player_base_crit_damage,
		related_nodes=[crit_node],
	)
	return result


def get_all_secondary_stats(player: PlayerModel) -> Stats:
	config = player.game_config
	result = Stats()
	for item in player.player_equipment_model.get_items().values():
		result.add_stat_contributions(item.secondary_stats, config)
	for pet in player.player_pet_collection_model.get_equipped_pets():
		result.add_stat_contributions(pet.secondary_stats, config)
	equipped_mount = _first_equipped_mount(player)
	if equipped_mount is not None:
		result.add_stat_contributions(equipped_mount.secondary_stats, config)
	return result


def get_ascension_stats(player: PlayerModel) -> Stats:
	config = player.game_config
	result = Stats()
	for ascension in (
		player.player_forge_model.ascension_model,
		player.player_skill_collection_model.ascension_model,
		player.player_pet_collection_model.ascension_model,
		player.player_mount_collection_model.ascension_model,
	):
		result.add_stat_contributions(ascension.get_level_stats(config))
	return result


def get_base_item_stats(
	game_config: Any,
	item_or_id: ItemModel | ItemId,
	level: int | None = None,
) -> dict[StatNode, int]:
	"""IL: PlayerModelItemExtensions.GetBaseItemStats — Dictionary<StatNode, FD6>."""
	from core.metaplaymath.config_values import stat_contribution_value_fd6_raw
	from core.metaplaymath.f64 import f64_to_raw
	from core.metaplaymath.fd6 import fd6_mul_f64_raw

	item_id, item_level = _coerce_item_id_and_level(item_or_id, level)
	balancing = _require_item_balancing(game_config)
	info = _require_equipment_info(game_config, item_id)
	scale_raw = f64_to_raw(balancing.level_scaling_base**item_level)

	out: dict[StatNode, int] = {}
	for row in _equipment_stat_rows(info):
		node = StatHelper.parse_stat_node(row)
		base_raw = stat_contribution_value_fd6_raw(row)
		value_raw = _scaled_base_row_value_fd6_raw(
			game_config, item_id, balancing, node, base_raw, scale_raw
		)
		if node in out:
			from core.metaplaymath.fd6 import fd6_add_raw

			out[node] = fd6_add_raw(out[node], value_raw)
		else:
			out[node] = value_raw
	return out


def get_resolved_item_stats(
	game_config: Any,
	item_or_id: ItemModel | ItemId,
	stats_that_affect_calculations: Stats,
	level: int | None = None,
) -> Stats:
	"""IL: PlayerModelItemExtensions.GetResolvedItemStats."""
	item_id, item_level = _coerce_item_id_and_level(item_or_id, level)
	balancing = _require_item_balancing(game_config)
	info = _require_equipment_info(game_config, item_id)
	scale = balancing.level_scaling_base**item_level

	result = Stats()
	weapon_info = None
	if item_id.Type == ItemType.Weapon:
		weapon_info = _require_weapon_info(game_config, item_id)

	for row in _equipment_stat_rows(info):
		node = StatHelper.parse_stat_node(row)
		from core.metaplaymath.config_values import stat_contribution_value_fd6_raw
		from core.metaplaymath.f64 import f64_to_raw
		from core.metaplaymath.fd6 import fd6_mul_f64_raw, fd6_to_double

		scale_raw = f64_to_raw(scale)
		value_raw = fd6_mul_f64_raw(scale_raw, stat_contribution_value_fd6_raw(row))
		stat_type = node.unique_stat.stat_type
		context: StatCalcContext | None = None

		if item_id.Type == ItemType.Weapon:
			if weapon_info is None:
				raise ValueError("weapon info required for weapon item stats")
			is_ranged = bool(weapon_info.get("IsRanged", False))
			if not is_ranged and stat_type == StatType.Damage:
				value_raw = fd6_mul_f64_raw(
					f64_to_raw(balancing.player_melee_damage_multiplier),
					value_raw,
				)
			target = StatTarget.equipment().with_item_type(ItemType.Weapon)
			context = StatCalcContext(is_ranged)
		else:
			target = StatTarget.equipment().with_item_type(item_id.Type)

		value = fd6_to_double(value_raw)

		resolved = StatHelper.calculate_value_from_stats(
			game_config,
			stats_that_affect_calculations,
			stat_type,
			target,
			value,
			context,
		)
		result.add_stat_contribution(node, resolved)
	return result


def _coerce_item_id_and_level(
	item_or_id: ItemModel | PlayerItemModel | ItemId,
	level: int | None,
) -> tuple[ItemId, int]:
	if isinstance(item_or_id, (ItemModel, PlayerItemModel)):
		return item_or_id.item_id, item_or_id.level
	if level is None:
		raise TypeError(
			"level is required when GetBaseItemStats/GetResolvedItemStats takes ItemId"
		)
	return item_or_id, level


def _require_item_balancing(game_config: Any):
	balancing = getattr(game_config, "item_balancing_config", None)
	if balancing is None:
		raise ValueError("item_balancing_config is required")
	return balancing


def _require_equipment_info(game_config: Any, item_id: ItemId) -> dict:
	items = getattr(game_config, "items", None)
	if items is None:
		raise ValueError("game_config.items is required")
	info = items.get(item_id)
	if info is None:
		raise ValueError(f"equipment info not found for {item_id!r}")
	return info


def _require_weapon_info(game_config: Any, item_id: ItemId) -> dict:
	weapons = getattr(game_config, "weapons", None)
	if weapons is None:
		raise ValueError("game_config.weapons is required")
	info = weapons.get(item_id)
	if info is None:
		raise ValueError(f"weapon info not found for {item_id!r}")
	return info


def _equipment_stat_rows(info: dict) -> list[dict]:
	rows = info.get("EquipmentStats")
	if rows is None:
		rows = info.get("Stats")
	return list(rows or [])


def _scaled_base_row_value_fd6_raw(
	game_config: Any,
	item_id: ItemId,
	balancing: Any,
	node: StatNode,
	base_raw: int,
	scale_raw: int,
) -> int:
	from core.metaplaymath.f64 import f64_to_raw
	from core.metaplaymath.fd6 import fd6_mul_f64_raw

	value_raw = fd6_mul_f64_raw(scale_raw, base_raw)
	if item_id.Type != ItemType.Weapon:
		return value_raw
	weapons = getattr(game_config, "weapons", None)
	if weapons is None:
		return value_raw
	weapon_info = weapons.get(item_id)
	if weapon_info is None or weapon_info.get("IsRanged", False):
		return value_raw
	if node.unique_stat.stat_type == StatType.Damage:
		mult_raw = f64_to_raw(balancing.player_melee_damage_multiplier)
		return fd6_mul_f64_raw(mult_raw, value_raw)
	return value_raw


def _first_equipped_mount(player: PlayerModel) -> PlayerMountModel | None:
	for mount in player.player_mount_collection_model.player_mount_models:
		if mount.is_equipped:
			return mount
	return None


def _add_skin_stat_contributions(
	skin_stats: Stats,
	skin: PlayerSkinModel,
	player: PlayerModel,
) -> None:
	contributions = get_resolved_stat_contributions(skin, player.game_config)
	skin_stats.add_stat_contributions(contributions)


def _merge_into_stats(target: Stats, source: Stats | SkillStats) -> None:
	target.add_stat_contributions(source)


PlayerModel.get_total_stats = get_total_stats
PlayerModel.calculate_total_stats = calculate_total_stats
PlayerModel.get_base_stats = get_base_stats
PlayerModel.get_all_secondary_stats = get_all_secondary_stats
PlayerModel.get_ascension_stats = get_ascension_stats
PlayerModel.get_base_item_stats = get_base_item_stats
PlayerModel.get_resolved_item_stats = get_resolved_item_stats
