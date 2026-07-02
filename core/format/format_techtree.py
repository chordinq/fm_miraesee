"""IL: TechTreeLocalizer + TechTreeNodeDetailsView.UpdateUi."""
from __future__ import annotations

from dataclasses import dataclass

from config import string_literal

from core.game_logic.enums import TechTreeNodeType
from core.game_logic.player.player_techtree_model import (
	_stat_value_at_level,
	lookup_upgrade_level_info,
)
from core.game_logic.stats.stat_helper import StatHelper

from .localizer_base import get_translation
from .number_format import format_percentage
from .stats_format import format_stat_delta_display, format_stat_display

_SINGLE_STAT_NODE_TYPES = (TechTreeNodeType.WeaponBonus, TechTreeNodeType.SkillDamage)

# IL TechTreeCategoryUiView — completion suffix parentheses + Complete key
_COMPLETE_LOC_KEY = string_literal(4898)
_PAREN_OPEN = string_literal(156)
_PAREN_CLOSE = string_literal(1271)

_TECH_NODE_TITLE_SUFFIX = "Title"
_TIER_ROMAN = ("I", "II", "III", "IV", "V")
_DELTA_OPEN = " ("
_DELTA_CLOSE = ")"


def parenthesized_text(inner: str) -> str:
	"""IL: StringLiteral_156 + text + StringLiteral_1271."""
	return f"{_PAREN_OPEN}{inner}{_PAREN_CLOSE}"


def format_tech_tree_category_progress(progress: float) -> str:
	"""IL: FormatMultiplier3SignificantDigits(progress*100) + StringLiteral_827."""
	return format_percentage(progress)


def format_tech_tree_complete_suffix(*, language: str | None = None) -> str:
	"""IL: parenthesized GetTranslation(StringLiteral_4898) → ``Complete``."""
	complete = get_translation(_COMPLETE_LOC_KEY, table="General", language=language)
	return parenthesized_text(complete)


def format_tech_tree_active_research_suffix(timer_text: str) -> str:
	"""IL: parenthesized TimeExtensions.Format(remaining)."""
	return parenthesized_text(timer_text)


@dataclass(frozen=True)
class TechTreeNodeDescriptionLine:
	text: str
	delta_text: str = ""


def get_tech_tree_node_title(node_type: TechTreeNodeType, *, language: str | None = None) -> str:
	"""IL: TechTreeLocalizer.NodeTitle — ``{Enum}Title``."""
	loc_key = f"{node_type.name}{_TECH_NODE_TITLE_SUFFIX}"
	return get_translation(loc_key, table="TechTree", language=language)


def tier_roman_numeral(tier: int) -> str:
	if 0 <= tier < len(_TIER_ROMAN):
		return _TIER_ROMAN[tier]
	return ""


def _tier_addition_value(lib_entry: dict, tier: int) -> float:
	tier_additions = lib_entry.get("TierAddition") or []
	if tier < 0 or tier >= len(tier_additions):
		return 0.0
	return float(tier_additions[tier])


def build_tech_tree_node_title(
	node_type: TechTreeNodeType,
	tier: int,
	*,
	language: str | None = None,
) -> str:
	"""IL: TechTreeLocalizer.NodeTitle + tier roman."""
	title = get_tech_tree_node_title(node_type, language=language)
	roman = tier_roman_numeral(tier)
	if not roman:
		return title
	return f"{title} {roman}"


def build_tech_tree_node_description_lines(
	lib_entry: dict,
	*,
	node_type: TechTreeNodeType,
	internal_level: int,
	level_max: int,
	tier: int,
	language: str | None = None,
) -> list[TechTreeNodeDescriptionLine]:
	"""IL: TechTreeNodeDetailsView__UpdateUi — one line per stat row."""
	stats = lib_entry.get("Stats") or []
	if not stats:
		return []

	lines: list[TechTreeNodeDescriptionLine] = []
	tier_bonus = _tier_addition_value(lib_entry, tier)
	max_internal = max(0, level_max - 1)
	single_stat_only = node_type in _SINGLE_STAT_NODE_TYPES

	for index, row in enumerate(stats):
		if single_stat_only:
			if index > 0:
				continue
		elif index > 0:
			lines.append(TechTreeNodeDescriptionLine(text=""))

		stat_node = StatHelper.parse_stat_node(row["StatNode"])
		if internal_level < 0:
			current_value = 0.0
		else:
			current_value = _stat_value_at_level(row, internal_level, tier_bonus)

		line_text = format_stat_display(
			stat_node,
			current_value,
			language=language,
			show_multipliers_as_percentage=True,
			show_value_at_end=True,
			show_operator_override=True,
		)

		delta_text = ""
		if 0 <= internal_level < max_internal:
			next_value = _stat_value_at_level(row, internal_level + 1, tier_bonus)
			delta = next_value - current_value
			if delta != 0.0:
				formatted = format_stat_delta_display(
					stat_node.unique_stat.stat_nature,
					delta,
					show_multipliers_as_percentage=True,
					show_operator_override=True,
				)
				delta_text = f"{_DELTA_OPEN}{formatted}{_DELTA_CLOSE}"

		lines.append(TechTreeNodeDescriptionLine(text=line_text, delta_text=delta_text))

	return lines


def build_tech_tree_node_description(
	lib_entry: dict,
	*,
	node_type: TechTreeNodeType,
	internal_level: int,
	level_max: int,
	tier: int,
	language: str | None = None,
) -> str:
	"""Plain-text fallback — concatenates base + delta without color."""
	parts: list[str] = []
	for line in build_tech_tree_node_description_lines(
		lib_entry,
		node_type=node_type,
		internal_level=internal_level,
		level_max=level_max,
		tier=tier,
		language=language,
	):
		if not line.text and not line.delta_text:
			parts.append("")
			continue
		parts.append(f"{line.text}{line.delta_text}")
	return "\n".join(parts)
