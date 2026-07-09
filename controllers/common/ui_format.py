from __future__ import annotations

from core.game_logic.enums import CurrencyType, SecondaryStatType, StatNature, StatType
from core.metaplaymath.fd6 import fd6_from_f64, fd6_truncate, format_fd6_raw
from core.format.number_format import (
	format_currency_value,
	format_multiplier,
	format_percentage,
	format_progress_pair,
	format_stat,
	max_progress_label,
	maxed_progress_label,
)
from core.format.numbers import format, format_long
from core.format.format_item import format_secondary_stats
from core.format.stats_format import (
	_assemble_stat_label_value,
	format_secondary_stat_display_value,
	format_stat_string,
	format_stat_value_string,
	get_stat_operator,
	should_show_operator,
)
from core.game_logic.stats.stat_target import StatTarget
from core.game_logic.config.shared_game_config import SharedGameConfig
from core.game_logic.stats.stat_helper import StatHelper
from ui.utils.ui_settings import game_number_formatting_enabled

_default_game_config: SharedGameConfig | None = None


def _game_config() -> SharedGameConfig:
	global _default_game_config
	if _default_game_config is None:
		_default_game_config = SharedGameConfig.load()
	return _default_game_config


def _format_secondary_stat_raw(
	stat_type: SecondaryStatType,
	value: float,
	game_config: SharedGameConfig,
) -> str:
	if value == 0.0:
		return ""

	row = game_config.secondary_stat_library.get(stat_type)
	if row is None:
		return ""

	stat_nodes = row.get("StatNodes") or []
	if not stat_nodes:
		return ""

	stat_node = StatHelper.parse_stat_node(stat_nodes[0])
	nature = stat_node.unique_stat.stat_nature
	fd6_value = fd6_from_f64(value)

	if nature == StatNature.Additive:
		operator = (
			get_stat_operator(nature, show_multipliers_as_percentage=True)
			if should_show_operator(nature)
			else ""
		)
		return f"{operator}{format_fd6_raw(fd6_value)}"

	operator = ""
	if should_show_operator(nature):
		operator = "-" if nature == StatNature.OneMinusMultiplier else "+"
	return f"{operator}{format_fd6_raw(fd6_value * 100.0)}%"


def format_ui_integer(value: int | float) -> str:
	if not game_number_formatting_enabled():
		return format_fd6_raw(float(value))
	if isinstance(value, int):
		return format_long(value)
	return format(float(value))


def format_ui_progress_pair(current: int | float, total: int | float) -> str:
	return format_progress_pair(
		current,
		total,
		format_value=format_ui_integer,
	)


def format_ui_max_progress_label() -> str:
	return max_progress_label()


def format_ui_maxed_progress_label(*, language: str | None = None) -> str:
	return maxed_progress_label(language=language)


def format_ui_percentage_fraction(value: float) -> str:
	if not game_number_formatting_enabled():
		return f"{format_fd6_raw(fd6_from_f64(value * 100.0))}%"
	return format_percentage(value)


def format_ui_percentage_rational(level_sum: int, max_sum: int) -> str:
	if max_sum < 1:
		return format_ui_percentage_fraction(0.0)
	if not game_number_formatting_enabled():
		return f"{format_fd6_raw(fd6_from_f64((level_sum * 100.0) / max_sum))}%"
	return format_percentage(level_sum / max_sum)


def format_ui_stat(value: float, *, as_multiplier: bool = False) -> str:
	if not game_number_formatting_enabled():
		return format_fd6_raw(fd6_truncate(value))
	return format_stat(value, digits=1 if as_multiplier else 0)


def _assemble_secondary_stat_line(label: str, value_text: str) -> str:
	if not label:
		return value_text
	if "{0}" in label:
		return label.format(value_text)
	return f"{value_text} {label}"


def format_ui_secondary_stat(
	stat_type: SecondaryStatType,
	value: float,
	*,
	game_config: SharedGameConfig | None = None,
) -> str:
	config = game_config if game_config is not None else _game_config()
	if game_number_formatting_enabled():
		return format_secondary_stat_display_value(stat_type, value, config)
	return _format_secondary_stat_raw(stat_type, value, config)


def _format_resolved_stat_value_raw(
	value: float,
	nature: StatNature,
	*,
	show_multipliers_as_percentage: bool = True,
) -> str:
	fd6_value = fd6_from_f64(value)
	show_operator = should_show_operator(nature)

	if nature == StatNature.Additive or not show_multipliers_as_percentage:
		if nature == StatNature.Multiplier:
			value_text = format_fd6_raw(fd6_value)
		else:
			value_text = format_fd6_raw(fd6_value)
		operator = (
			get_stat_operator(nature, show_multipliers_as_percentage)
			if show_operator
			else ""
		)
	else:
		operator = ""
		if show_operator:
			operator = "-" if nature == StatNature.OneMinusMultiplier else "+"
		value_text = f"{format_fd6_raw(fd6_value * 100.0)}%"
	return f"{operator}{value_text}"


def format_ui_attack_speed_stat(value: float) -> str:
	base = fd6_from_f64(value)
	bonus = fd6_from_f64(value - 1.0)
	if game_number_formatting_enabled():
		return f"×{format_multiplier(base, 2)} ({format_percentage(bonus)})"
	return f"×{format_fd6_raw(base)} (+{format_fd6_raw(bonus * 100.0)}%)"


def format_ui_resolved_stat_line(
	stat_type: StatType,
	value: float,
	nature: StatNature,
	*,
	language: str | None = None,
	show_multipliers_as_percentage: bool = True,
) -> str:
	if stat_type is StatType.AttackSpeed:
		value_text = format_ui_attack_speed_stat(value)
	elif game_number_formatting_enabled():
		value_text = format_stat_value_string(
			fd6_from_f64(value),
			nature,
			show_multipliers_as_percentage=show_multipliers_as_percentage,
		)
	else:
		value_text = _format_resolved_stat_value_raw(
			value,
			nature,
			show_multipliers_as_percentage=show_multipliers_as_percentage,
		)
	label = format_stat_string(
		stat_type,
		StatTarget.player(),
		language=language,
	)
	return _assemble_stat_label_value(
		label,
		value_text,
		show_value_at_end=False,
	)


def format_ui_secondary_stat_line(
	stat_type: SecondaryStatType,
	value: float,
	*,
	game_config: SharedGameConfig | None = None,
	language: str | None = None,
) -> str:
	config = game_config if game_config is not None else _game_config()
	if game_number_formatting_enabled():
		return format_secondary_stats(
			stat_type,
			value,
			config,
			language=language,
		)

	if value == 0.0:
		return ""

	row = config.secondary_stat_library.get(stat_type)
	if row is None:
		return ""

	stat_nodes = row.get("StatNodes") or []
	if not stat_nodes:
		return ""

	stat_node = StatHelper.parse_stat_node(stat_nodes[0])
	label = format_stat_string(
		stat_node.unique_stat.stat_type,
		stat_node.target,
		condition=stat_node.condition,
		language=language,
	)
	value_text = _format_secondary_stat_raw(stat_type, value, config)
	return _assemble_secondary_stat_line(label, value_text)


def format_ui_percentage(value: float, *, positive: bool = True) -> str:
	if not game_number_formatting_enabled():
		text = f"{format_fd6_raw(fd6_from_f64(value) * 100.0)}%"
	else:
		text = format_percentage(value)
	if positive and not text.startswith("+"):
		return f"+{text}"
	if not positive and not text.startswith("-"):
		return f"-{text}"
	return text


def format_ui_dungeon_percent(value: float) -> str:
	if not game_number_formatting_enabled():
		return f"{format_fd6_raw(fd6_truncate(value * 100.0))}%"
	return format_stat(value * 100.0, digits=0)


def format_ui_currency(
	amount: int | float,
	currency_type: CurrencyType,
	*,
	icon_prefix: str = "",
) -> str:
	if not game_number_formatting_enabled():
		text = format_fd6_raw(float(amount))
	elif isinstance(amount, int):
		text = format_currency_value(amount)
	else:
		text = format_currency_value(float(amount))
	if icon_prefix:
		return icon_prefix + text
	return text
