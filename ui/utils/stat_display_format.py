from __future__ import annotations

from core.game_logic.enums import SecondaryStatType, StatNature
from core.game_logic.fd6_math import fd6_from_f64, fd6_truncate, format_fd6_raw
from core.game_logic.number_format import format_stat
from core.game_logic.shared_game_config import SharedGameConfig
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stats_format import (
	format_secondary_stat_display_value,
	get_stat_operator,
	should_show_operator,
)
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


def format_ui_stat(value: float, *, as_multiplier: bool = False) -> str:
	if not game_number_formatting_enabled():
		return format_fd6_raw(fd6_truncate(value))
	return format_stat(value, digits=1 if as_multiplier else 0)


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


def format_ui_percentage(value: float, *, positive: bool = True) -> str:
	from core.game_logic.number_format import format_percentage

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
