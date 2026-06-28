from __future__ import annotations
from typing import TYPE_CHECKING, Any
from ..enums import AttackType, ItemType, SecondaryStatType, StatType
from ..shared_game_config import SharedGameConfig
from ..stats import StatNode, Stats
from ..stats.skill_stats import SkillStats
from ..stats.stat_helper import StatHelper
from ..stats.stat_target import EquipmentStatTarget, PlayerStatTarget, WeaponStatTarget
from .player_equipment_model import ItemId, ItemModel
from .player_item_model import PlayerItemModel
from .player_mount_collection_model import PlayerMountModel
from .player_skin_collection_model import PlayerSkinModel

if TYPE_CHECKING:
	from .player_model import PlayerModel

_FD6_SCALE = 1_000_000


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
		_add_skin_stat_contributions(skin_stats, skin, player, total_stats)

	sets_stats = Stats()
	for bonus in player.sets_model.all_active_set_bonus_tiers(player.game_config):
		bonus_stats = getattr(bonus, "stats", None)
		if bonus_stats is None and isinstance(bonus, dict):
			bonus_stats = bonus.get("Stats")
		if bonus_stats is not None:
			sets_stats.add_stat_contributions(bonus_stats)

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
	target = PlayerStatTarget()
	result.add_stat_contribution(
		StatHelper.new_additive_stat_node(StatType.Damage, target),
		balancing.player_base_damage,
	)
	result.add_stat_contribution(
		StatHelper.new_additive_stat_node(StatType.Health, target),
		balancing.player_base_health,
	)
	crit_node = StatHelper.new_multiplicative_node(
		StatType.CriticalDamage, PlayerStatTarget()
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
) -> dict[StatNode, float]:
	item_id, item_level = _coerce_item_id_and_level(item_or_id, level)
	balancing = _require_item_balancing(game_config)
	info = _require_equipment_info(game_config, item_id)
	scale = balancing.level_scaling_base**item_level

	out: dict[StatNode, float] = {}
	for row in _equipment_stat_rows(info):
		node = StatHelper.parse_stat_node(row)
		value = _scaled_base_row_value(
			game_config, item_id, balancing, node, float(row.get("Value", 0.0)), scale
		)
		out[node] = out.get(node, 0.0) + value
	return out


def get_resolved_item_stats(
	game_config: Any,
	item_or_id: ItemModel | ItemId,
	stats_that_affect_calculations: Stats,
	level: int | None = None,
) -> Stats:
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
		value = float(row.get("Value", 0.0)) * scale
		stat_type = node.unique_stat.stat_type
		is_ranged: bool | None = None

		if item_id.Type == ItemType.Weapon:
			if weapon_info is None:
				raise ValueError("weapon info required for weapon item stats")
			if not weapon_info.get("IsRanged", False):
				if stat_type == StatType.Damage:
					value *= balancing.player_melee_damage_multiplier
			is_ranged = bool(weapon_info.get("IsRanged", False))
			target: EquipmentStatTarget | WeaponStatTarget = WeaponStatTarget(
				AttackType.Ranged if is_ranged else AttackType.Melee
			)
		else:
			target = EquipmentStatTarget(item_id.Type)

		resolved = StatHelper.calculate_value_from_stats(
			game_config,
			stats_that_affect_calculations,
			stat_type,
			target,
			value,
			is_ranged,
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
		raise TypeError("level is required when GetBaseItemStats/GetResolvedItemStats takes ItemId")
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


def _scaled_base_row_value(
	game_config: Any,
	item_id: ItemId,
	balancing: Any,
	node: StatNode,
	base_value: float,
	scale: float,
) -> float:
	value = base_value * scale
	if item_id.Type != ItemType.Weapon:
		return value
	weapons = getattr(game_config, "weapons", None)
	if weapons is None:
		return value
	weapon_info = weapons.get(item_id)
	if weapon_info is None or weapon_info.get("IsRanged", False):
		return value
	if node.unique_stat.stat_type == StatType.Damage:
		return value * balancing.player_melee_damage_multiplier
	return value


def _first_equipped_mount(player: PlayerModel) -> PlayerMountModel | None:
	for mount in player.player_mount_collection_model.player_mount_models:
		if mount.is_equipped:
			return mount
	return None


def _add_skin_stat_contributions(
	skin_stats: Stats,
	skin: PlayerSkinModel,
	player: PlayerModel,
	total_stats: Stats,
) -> None:
	# IL: <>c__DisplayClass5_0.<CalculateTotalStats>b__2(PlayerSkinModel)
	# TODO: requires IL dump — no-op until dump provides skin data
	pass


def _merge_into_stats(target: Stats, source: Stats | SkillStats) -> None:
	if isinstance(source, SkillStats):
		for node, raw_fd6 in source.stats.items():
			target.add_stat_contribution(node, raw_fd6 / _FD6_SCALE)
		return
	target.add_stat_contributions(source)


_STAT_JOIN = " & "


def format_secondary_stats(
	stat_type: SecondaryStatType,
	calculated_value: float,
	game_config: SharedGameConfig,
) -> str:
	"""IL: PlayerItemModelExtensions.FormatSecondaryStats(SecondaryStatType, FD6)"""
	from ..fd6_math import fd6_from_f64
	from ..stats.stats_format import format_stat_node, get_stat_name

	row = game_config.secondary_stat_library.get(stat_type)
	if row is None:
		raise NotImplementedError(
			"PlayerItemModelExtensions.FormatSecondaryStats: missing SecondaryStatLibrary row"
		)

	stat_nodes = row.get("StatNodes") or []
	if not stat_nodes:
		raise NotImplementedError(
			"PlayerItemModelExtensions.FormatSecondaryStats: missing StatNodes"
		)

	result = ""
	for index, node_data in enumerate(stat_nodes):
		if stat_type in (
			SecondaryStatType.SkillDamageMulti,
			SecondaryStatType.DamageMulti,
		) and index > 0:
			continue
		if (
			stat_type not in (
				SecondaryStatType.SkillDamageMulti,
				SecondaryStatType.DamageMulti,
			)
			or index == 0
		):
			if calculated_value == 0.0:
				continue
			stat_node = StatHelper.parse_stat_node(node_data)
			if index == 0:
				result += format_stat_node(
					stat_node,
					fd6_from_f64(calculated_value),
					show_multipliers_as_percentage=True,
					show_value_at_end=False,
				)
			else:
				result += _STAT_JOIN + get_stat_name(stat_node.unique_stat.stat_type)
	return result


def format_secondary_stats_collection(
	secondary_stats,
	game_config: SharedGameConfig,
) -> str:
	"""IL: PlayerItemModelExtensions.FormatSecondaryStats(SecondaryStats)"""
	lines: list[str] = []
	for stat_type in secondary_stats.interpolated_stat_values.keys():
		found, resolved = secondary_stats.try_get_stat_value(stat_type, game_config)
		if not found:
			continue
		line = format_secondary_stats(stat_type, resolved, game_config)
		if line:
			lines.append(line)
	return "\n".join(lines)
