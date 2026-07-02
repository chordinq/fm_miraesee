from __future__ import annotations

from typing import TYPE_CHECKING

from core.game_logic.enums import (
	ItemType,
	StatCondition,
	StatNature,
	StatTargetKind,
	StatType,
)
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stats import StatNode
from core.metaplaymath.fd6 import fd6_from_f64

from .localizer_base import get_translation
from .number_format import format_multiplier, format_percentage, format_stat as format_number_stat
from .stats_localizer import (
	get_attack_type_name,
	get_condition_name,
	get_dungeon_drop_text,
	get_stat_type_name,
	translate_stat_target,
)

if TYPE_CHECKING:
	from core.game_logic.config.shared_game_config import SharedGameConfig

_PLACEHOLDER = "{0}"
_SPACE = " "
_BONUS_LOC_KEY = "Bonus"


def should_show_operator(
	nature: StatNature,
	show_operator_override: bool | None = None,
) -> bool:
	"""IL: StatsFormat.ShouldShowOperator — default: nature != Additive."""
	if show_operator_override is not None:
		return show_operator_override
	return nature != StatNature.Additive


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
			value_text = format_number_stat(fd6_value, digits=0)
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


def get_stat_name(stat_type: StatType, *, language: str | None = None) -> str:
	"""IL: StatsFormat.GetStatName → StatsLocalizer.GetStatName."""
	return get_stat_type_name(stat_type, language=language)


def _condition_prefix(condition: StatCondition, *, language: str | None = None) -> str:
	"""IL: StatsFormat.<>g__ConditionPrefix|11_0."""
	if condition == StatCondition.None_:
		return ""
	name = get_condition_name(condition, language=language)
	if not name:
		return ""
	return f"{name}{_SPACE}"


def _bonus_text(*, language: str | None = None) -> str:
	return get_translation(_BONUS_LOC_KEY, table="General", language=language)


def _join_label_parts(*parts: str) -> str:
	return _SPACE.join(part for part in parts if part)


def _target_bonus_stat_label(
	target_text: str,
	stat_type: StatType,
	*,
	language: str | None = None,
	bonus_text: str | None = None,
) -> str:
	bonus = _bonus_text(language=language) if bonus_text is None else bonus_text
	return _join_label_parts(target_text, bonus, get_stat_name(stat_type, language=language))


def _single_stats_translation(key: str, *, language: str | None = None) -> str:
	return get_translation(key, table="Stats", language=language)


def format_stat_string(
	stat_type: StatType,
	target,
	*,
	condition: StatCondition = StatCondition.None_,
	language: str | None = None,
) -> str:
	"""IL: StatsFormat.FormatStatString(StatType, StatTarget, StatCondition)."""
	from core.game_logic.enums import AttackType, CurrencyType, DungeonType
	from core.game_logic.stats.stat_target import StatTarget

	if not isinstance(target, StatTarget):
		raise TypeError("format_stat_string requires StatTarget")

	target_text = translate_stat_target(target, language=language)
	kind = target.kind

	if kind == StatTargetKind.Player:
		prefix = _condition_prefix(condition, language=language)
		return prefix + get_stat_name(stat_type, language=language)

	if kind == StatTargetKind.Equipment:
		item_type_value = None
		attack_type_value = None
		for qualifier in target.qualifiers:
			if qualifier.type.name == "ItemType":
				item_type_value = qualifier.value
			elif qualifier.type.name == "AttackType":
				attack_type_value = qualifier.value
		if item_type_value == int(ItemType.Weapon) and stat_type == StatType.Damage:
			if attack_type_value is not None:
				attack_name = get_attack_type_name(
					AttackType(attack_type_value),
					language=language,
				)
				return f"{attack_name}{_SPACE}{get_stat_name(stat_type, language=language)}"
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	if kind == StatTargetKind.ActiveSkill:
		if stat_type == StatType.Cost:
			return _single_stats_translation("Cooldown", language=language)
		if stat_type == StatType.TimerSpeed:
			target_text = translate_stat_target(target, language=language)
			cooldown_text = _single_stats_translation("Cooldown", language=language)
			return _join_label_parts(target_text, cooldown_text)
		if stat_type == StatType.MaxCount:
			return _target_bonus_stat_label(
				target_text,
				stat_type,
				language=language,
				bonus_text=_single_stats_translation("Summon", language=language),
			)
		target_text = translate_stat_target(target, language=language)
		stat_name = get_stat_name(stat_type, language=language)
		return _join_label_parts(target_text, stat_name)

	if kind == StatTargetKind.PassiveSkill:
		return _target_bonus_stat_label(
			target_text,
			stat_type,
			language=language,
			bonus_text=_single_stats_translation("Base", language=language),
		)

	if kind == StatTargetKind.Mount:
		if stat_type == StatType.FreebieChance:
			return _single_stats_translation("MountFreebieChanceDesc", language=language)
		if stat_type == StatType.MaxCount:
			return _target_bonus_stat_label(
				target_text,
				stat_type,
				language=language,
				bonus_text=_single_stats_translation("Summon", language=language),
			)
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	if kind == StatTargetKind.Forge:
		if stat_type == StatType.MaxCount:
			return _single_stats_translation("ForgeNumberOfHammers", language=language)
		if stat_type == StatType.FreebieChance:
			return _single_stats_translation("ForgeFreebieChanceDesc", language=language)
		return _target_bonus_stat_label(
			target_text,
			stat_type,
			language=language,
			bonus_text=_single_stats_translation("Upgrade", language=language),
		)

	if kind == StatTargetKind.Egg:
		if stat_type == StatType.FreebieChance:
			return _single_stats_translation("EggsFreebieChanceDesc", language=language)
		if stat_type == StatType.TimerSpeed:
			return _target_bonus_stat_label(
				target_text,
				stat_type,
				language=language,
				bonus_text=_single_stats_translation("Hatch", language=language),
			)
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	if kind == StatTargetKind.Currency:
		dungeon_value = None
		currency_value = None
		for qualifier in target.qualifiers:
			if qualifier.type.name == "DungeonType":
				dungeon_value = qualifier.value
			elif qualifier.type.name == "CurrencyType":
				currency_value = qualifier.value

		if dungeon_value is not None and currency_value is not None:
			if stat_type == StatType.Bonus:
				return get_dungeon_drop_text(
					DungeonType(dungeon_value),
					CurrencyType(currency_value),
					language=language,
				)
		if dungeon_value is not None and currency_value is None:
			return get_dungeon_drop_text(DungeonType(dungeon_value), language=language)

		if dungeon_value is None and currency_value is not None:
			return _target_bonus_stat_label(
				target_text,
				stat_type,
				language=language,
				bonus_text=_single_stats_translation("Dungeon", language=language),
			)

		return _join_label_parts(
			target_text,
			get_stat_name(stat_type, language=language),
		)

	if kind == StatTargetKind.Pet:
		if stat_type == StatType.MaxLevel:
			return _target_bonus_stat_label(
				target_text,
				StatType.MaxLevel,
				language=language,
				bonus_text=_single_stats_translation("LevelUpRequirement", language=language),
			)
		if stat_type == StatType.MaxCount:
			return _target_bonus_stat_label(
				target_text,
				stat_type,
				language=language,
				bonus_text=_single_stats_translation("Summon", language=language),
			)
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	if kind == StatTargetKind.TechTree:
		if stat_type == StatType.MaxCount:
			return _join_label_parts(
				_single_stats_translation("TechNodeUpgrade", language=language),
				get_stat_name(StatType.MaxCount, language=language),
			)
		if stat_type == StatType.Cost:
			return _join_label_parts(
				_single_stats_translation("TechResearch", language=language),
				get_stat_name(StatType.Cost, language=language),
			)
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	if kind == StatTargetKind.Duration:
		if stat_type == StatType.Bonus:
			return _join_label_parts(
				_single_stats_translation("MaxUpper", language=language),
				get_stat_name(stat_type, language=language),
			)
		return _target_bonus_stat_label(target_text, stat_type, language=language)

	return _target_bonus_stat_label(target_text, stat_type, language=language)


def format_stat_node(
	stat_node: StatNode,
	value: float,
	*,
	show_multipliers_as_percentage: bool = False,
	show_value_at_end: bool = False,
	show_operator_override: bool | None = None,
	language: str | None = None,
) -> str:
	"""IL: StatsFormat.FormatStat(StatNode, FD6, bool, bool, Nullable<bool>)."""
	label = format_stat_string(
		stat_node.unique_stat.stat_type,
		stat_node.target,
		condition=stat_node.condition,
		language=language,
	)
	value_text = format_stat_value_string(
		value,
		stat_node.unique_stat.stat_nature,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_operator_override=show_operator_override,
	)
	return _assemble_stat_label_value(
		label,
		value_text,
		show_value_at_end=show_value_at_end,
	)


def format_stat_delta_display(
	stat_nature: StatNature,
	delta: float,
	*,
	show_multipliers_as_percentage: bool = True,
	show_operator_override: bool = True,
) -> str:
	"""IL: StatsFormat.FormatStat(FD6, StatNature, …) value-only overload."""
	return format_stat_value_string(
		delta,
		stat_nature,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_operator_override=show_operator_override,
	)


def format_stat_display(
	stat_node: StatNode,
	value: float,
	*,
	language: str | None = None,
	show_multipliers_as_percentage: bool = True,
	show_value_at_end: bool = True,
	show_operator_override: bool = True,
) -> str:
	"""IL: StatsFormat.FormatStat — label + value assembly."""
	label = format_stat_string(
		stat_node.unique_stat.stat_type,
		stat_node.target,
		condition=stat_node.condition,
		language=language,
	)
	value_text = format_stat_value_string(
		value,
		stat_node.unique_stat.stat_nature,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_operator_override=show_operator_override,
	)
	return _assemble_stat_label_value(
		label,
		value_text,
		show_value_at_end=show_value_at_end,
	)


def _assemble_stat_label_value(
	label: str,
	value_text: str,
	*,
	show_value_at_end: bool,
) -> str:
	if not label:
		return value_text
	if _PLACEHOLDER in label:
		return label.format(value_text)
	if show_value_at_end:
		return f"{label}{_SPACE}{value_text}"
	return f"{value_text}{_SPACE}{label}"


def format_secondary_stat_display_value(
	stat_type,
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


_DELTA_OPEN_POSITIVE = "(+"
_DELTA_OPEN_NEGATIVE = "(-"
_DELTA_CLOSE = ")"


def format_stat_comparison_flat(
	stat_node: StatNode,
	current_value: float,
	target_value: float,
	*,
	show_multipliers_as_percentage: bool = False,
) -> str:
	"""IL: GameContextExtensions.FormatStatComparisonFlat."""
	delta = target_value - current_value
	base_line = format_stat_node(
		stat_node,
		current_value,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_value_at_end=False,
		show_operator_override=False,
	)
	if delta == 0.0:
		return base_line

	delta_text = format_stat_value_string(
		delta,
		stat_node.unique_stat.stat_nature,
		show_multipliers_as_percentage=show_multipliers_as_percentage,
		show_operator_override=False,
	)
	if delta > 0.0:
		suffix = f"{_DELTA_OPEN_POSITIVE}{delta_text}{_DELTA_CLOSE}"
	else:
		suffix = f"{_DELTA_OPEN_NEGATIVE}{delta_text}{_DELTA_CLOSE}"
	return f"{base_line}  {suffix}"
