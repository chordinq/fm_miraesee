"""IL: StatsLocalizer (TypeDefIndex 7095)."""
from __future__ import annotations

from core.game_logic.enums import (
	AttackType,
	CombatSkill,
	CurrencyType,
	DungeonType,
	ItemType,
	Rarity,
	Source,
	StatCondition,
	StatQualifierType,
	StatTargetKind,
	StatType,
)
from core.game_logic.stats.stat_target import StatTarget

from .localizer import get_currency_name, get_dungeon_name, get_rarity_name
from .localizer_base import get_translation, localize

_SPACE = " "


def get_stat_type_name(stat_type: StatType, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.GetStatName."""
	return get_translation(stat_type.name, table="Stats", language=language)


def get_attack_type_name(attack_type: AttackType, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.GetAttackTypeName."""
	return get_translation(attack_type.name, table="Stats", language=language)


def get_item_type_name(item_type: ItemType, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.GetItemTypeName."""
	return get_translation(item_type.name, table="Stats", language=language)


def get_condition_name(condition: StatCondition, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.GetConditionName."""
	if condition == StatCondition.None_:
		return ""
	return get_translation(condition.name, table="Stats", language=language)


def _qualifier_enum(target: StatTarget, qualifier_type: StatQualifierType) -> int | None:
	for qualifier in target.qualifiers:
		if qualifier.type == qualifier_type:
			return qualifier.value
	return None


def _has_qualifier(target: StatTarget, qualifier_type: StatQualifierType) -> bool:
	return _qualifier_enum(target, qualifier_type) is not None


def _concat(prefix: str, suffix: str) -> str:
	if not prefix:
		return suffix
	if not suffix:
		return prefix
	return f"{prefix}{_SPACE}{suffix}"


def get_dungeon_text(target: StatTarget, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.GetDungeonText (private)."""
	dungeon_value = _qualifier_enum(target, StatQualifierType.DungeonType)
	currency_value = _qualifier_enum(target, StatQualifierType.CurrencyType)

	if dungeon_value is None:
		dungeon_part = get_translation("Dungeons", table="Stats", language=language)
	else:
		dungeon_part = get_dungeon_name(DungeonType(dungeon_value), language=language)

	if currency_value is None:
		currency_part = get_translation("Currency", table="Stats", language=language)
	else:
		currency_part = get_currency_name(CurrencyType(currency_value), language=language)

	return f"{dungeon_part}{_SPACE}{currency_part}"


def get_dungeon_drop_text(
	dungeon: DungeonType,
	currency: CurrencyType | None = None,
	*,
	language: str | None = None,
) -> str:
	"""IL: StatsLocalizer.GetDungeonDropText."""
	dungeon_name = get_dungeon_name(dungeon, language=language)
	if currency is None:
		currency_label = get_translation("Currency", table="Stats", language=language)
	else:
		currency_label = get_currency_name(currency, language=language)
	return localize("XDungeonDropY", dungeon_name, currency_label, table="Stats", language=language)


def translate_stat_target(target: StatTarget, *, language: str | None = None) -> str:
	"""IL: StatsLocalizer.TranslateStatTarget."""
	kind = target.kind

	if kind == StatTargetKind.Player:
		return ""

	if kind == StatTargetKind.Equipment:
		item_type_value = _qualifier_enum(target, StatQualifierType.ItemType)
		if item_type_value is not None:
			if item_type_value == int(ItemType.Weapon):
				attack_type_value = _qualifier_enum(target, StatQualifierType.AttackType)
				if attack_type_value is not None:
					return get_attack_type_name(
						AttackType(attack_type_value),
						language=language,
					)
				return get_translation("Weapon", table="Stats", language=language)
			return get_item_type_name(ItemType(item_type_value), language=language)
		return get_translation("Equipment", table="Stats", language=language)

	if kind == StatTargetKind.ActiveSkill:
		skill_value = _qualifier_enum(target, StatQualifierType.Skill)
		skill_name = ""
		if skill_value is not None:
			skill_name = get_translation(
				CombatSkill(skill_value).name,
				table="Skills",
				language=language,
			)
		suffix = get_translation("Skill", table="Stats", language=language)
		return _concat(skill_name, suffix)

	if kind == StatTargetKind.PassiveSkill:
		skill_value = _qualifier_enum(target, StatQualifierType.Skill)
		skill_name = ""
		if skill_value is not None:
			skill_name = get_translation(
				CombatSkill(skill_value).name,
				table="Skills",
				language=language,
			)
		suffix = get_translation("SkillPassive", table="Stats", language=language)
		return _concat(skill_name, suffix)

	if kind in (StatTargetKind.Mount, StatTargetKind.Egg, StatTargetKind.Pet):
		rarity_value = _qualifier_enum(target, StatQualifierType.Rarity)
		rarity_name = ""
		if rarity_value is not None:
			rarity_name = get_rarity_name(Rarity(rarity_value), language=language)
		suffix_key = {
			StatTargetKind.Mount: "Mounts",
			StatTargetKind.Egg: "Egg",
			StatTargetKind.Pet: "Pet",
		}[kind]
		suffix = get_translation(suffix_key, table="Stats", language=language)
		return _concat(rarity_name, suffix)

	if kind == StatTargetKind.Forge:
		return get_translation("Forge", table="Stats", language=language)

	if kind == StatTargetKind.Currency:
		if _has_qualifier(target, StatQualifierType.DungeonType):
			return get_dungeon_text(target, language=language)

		source_value = _qualifier_enum(target, StatQualifierType.Source)
		currency_value = _qualifier_enum(target, StatQualifierType.CurrencyType)

		if source_value == int(Source.Offline):
			if currency_value is not None:
				currency_name = get_currency_name(
					CurrencyType(currency_value),
					language=language,
				)
				offline_suffix = get_translation(
					"OfflineCurrencyReward",
					table="Stats",
					language=language,
				)
				return _concat(currency_name, offline_suffix)
			return get_translation("OfflineReward", table="Stats", language=language)

		if currency_value is not None:
			return get_currency_name(CurrencyType(currency_value), language=language)

		return get_translation("Currency", table="Stats", language=language)

	if kind == StatTargetKind.TechTree:
		return get_translation("TechTree", table="Stats", language=language)

	if kind == StatTargetKind.Duration:
		return get_translation("OfflineRewardTime", table="Stats", language=language)

	return ""
