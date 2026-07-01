from __future__ import annotations

from core.game_logic.enums import SecondaryStatType
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stat_helper import StatHelper
from core.metaplaymath.fd6 import fd6_from_f64

from .stats_format import format_stat_node, get_stat_name

_STAT_JOIN = " & "


def format_secondary_stats(
	stat_type: SecondaryStatType,
	calculated_value: float,
	game_config: SharedGameConfig,
) -> str:
	"""IL: PlayerItemModelExtensions.FormatSecondaryStats(SecondaryStatType, FD6)"""
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
			stat_type
			not in (
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
