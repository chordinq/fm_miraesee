from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import SecondaryStatType, StatNature, StatType
from core.fd6_math import fd6_from_f64
from ..number_format import format_multiplier, format_percentage, format_stat
from .stat_helper import StatHelper
from .stats import StatNode

if TYPE_CHECKING:
	from ..shared_game_config import SharedGameConfig


def should_show_operator(
	nature: StatNature,
	show_operator_override: bool | None = None,
) -> bool:
	"""IL: StatsFormat.ShouldShowOperator(StatNature, Nullable<bool>)"""
	if show_operator_override is not None:
		return show_operator_override
	return nature in (
		StatNature.Multiplier,
		StatNature.OneMinusMultiplier,
		StatNature.Additive,
		StatNature.Divisor,
	)


def get_stat_operator(nature: StatNature, show_multipliers_as_percentage: bool) -> str:
	"""IL: StatsFormat.GetStatOperator(StatNature, bool showMultipliersAsPercentage)"""
	if not show_multipliers_as_percentage:
		if nature == StatNature.Multiplier:
			return "x"
		return ""
	if nature == StatNature.OneMinusMultiplier:
		return "-"
	if nature in (StatNature.Multiplier, StatNature.Additive, StatNature.Divisor):
		return "+"
	return ""


def format_stat_value_string(
	value: float,
	nature: StatNature,
	*,
	show_multipliers_as_percentage: bool = False,
	show_operator_override: bool | None = None,
) -> str:
	"""IL: StatsFormat.FormatStatValueString(FD6, StatNature, bool, Nullable<bool>)"""
	fd6_value = value
	if nature == StatNature.Multiplier and not show_multipliers_as_percentage:
		fd6_value = value + 1.0

	show_operator = should_show_operator(nature, show_operator_override)

	if nature == StatNature.Additive or not show_multipliers_as_percentage:
		if nature == StatNature.Multiplier:
			value_text = format_multiplier(fd6_value, 2)
		else:
			value_text = format_stat(fd6_value, digits=0)
		operator = (
			get_stat_operator(nature, show_multipliers_as_percentage)
			if show_operator
			else ""
		)
	else:
		if show_operator:
			operator = (
				"-"
				if nature == StatNature.OneMinusMultiplier
				else "+"
			)
		else:
			operator = ""
		value_text = format_percentage(fd6_value)

	return f"{operator}{value_text}"


def get_stat_name(stat_type: StatType) -> str:
	"""IL: StatsFormat.GetStatName(StatType) — UI uses loc; not needed for value-only display."""
	return stat_type.name


def format_stat_node(
	stat_node: StatNode,
	value: float,
	*,
	show_multipliers_as_percentage: bool = False,
	show_value_at_end: bool = False,
	show_operator_override: bool | None = None,
) -> str:
	"""IL: StatsFormat.FormatStat(StatNode, FD6, bool, bool, Nullable<bool>)"""
	value_text = format_stat_value_string(
		value,
		stat_node.unique_stat.stat_nature,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_operator_override=show_operator_override,
	)
	if show_value_at_end:
		name = get_stat_name(stat_node.unique_stat.stat_type)
		return f"{value_text}{name}"
	return value_text


def format_secondary_stat_display_value(
	stat_type: SecondaryStatType,
	calculated_value: float,
	game_config: SharedGameConfig,
) -> str:
	"""Value column for split UI: first StatNode FormatStat only (labels are separate loc)."""
	if calculated_value == 0.0:
		return ""

	row = game_config.secondary_stat_library.get(stat_type)
	if row is None:
		return ""

	stat_nodes = row.get("StatNodes") or []
	if not stat_nodes:
		return ""

	stat_node = StatHelper.parse_stat_node(stat_nodes[0])
	return format_stat_node(
		stat_node,
		fd6_from_f64(calculated_value),
		show_multipliers_as_percentage=True,
		show_value_at_end=False,
	)
