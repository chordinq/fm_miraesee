from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Property, QObject, Signal, Slot

from config import ITEMS_MAPPING
from controllers.common.ui_format import (
	format_ui_resolved_stat_line,
	format_ui_secondary_stat_line,
)
from core.format.localizer_base import get_localized, selected_language
from core.game_logic.enums import SecondaryStatType, StatNature, StatType
from core.game_logic.player.player_equipment_model import ItemId, ItemModel
from core.game_logic.player.player_model import PlayerModel, get_total_stats
from core.game_logic.stats.stat_target import StatTarget
from core.metaplaymath.f64 import f64_to_raw
from core.metaplaymath.fd6 import fd6_from_f64, fd6_from_f64_raw, fd6_sub_raw, fd6_to_double
from ui.utils.localizer import name_loc_from_entry
from utils.combat.attack_cycle import (
	analytic_cycle_metrics,
	attack_speed_breakpoint_rows,
	weapon_timing_from_library,
)


def _text_row(text: str, *, secondary: bool = False) -> dict[str, object]:
	return {"text": text, "secondary": secondary}


def _secondary_display_value(
	stat_type: SecondaryStatType,
	value: float,
	base_crit_bonus: float,
) -> float:
	display_value = float(value)
	if stat_type is SecondaryStatType.CriticalMulti and base_crit_bonus > 0.0:
		display_value = fd6_to_double(
			fd6_sub_raw(
				fd6_from_f64_raw(f64_to_raw(display_value)),
				fd6_from_f64_raw(f64_to_raw(base_crit_bonus)),
			)
		)
	return fd6_from_f64(display_value)


def _item_mapping_key(item_id: ItemId) -> str:
	return f"{item_id.Age.value}_{item_id.Type.value}_{item_id.Idx}"


_PROFILE_COMBAT_STAT_TYPES: tuple[StatType, ...] = (
	StatType.AttackSpeed,
	StatType.CriticalChance,
	StatType.CriticalDamage,
	StatType.BlockChance,
	StatType.HealthRegen,
	StatType.LifeSteal,
	StatType.DoubleDamageChance,
	StatType.MoveSpeed,
)


def _stat_config_row(config, stat_type: StatType) -> tuple[StatNature, dict] | None:
	for nature in StatNature:
		row = config.stat_config_library.get((stat_type, nature))
		if row is not None:
			return nature, row
	return None


def _resolved_player_stat_value(
	stats,
	config,
	stat_type: StatType,
	nature: StatNature,
) -> float:
	"""IL: default + sum(Player-target contributions for stat/nature)."""
	from core.metaplaymath.fd6 import fd6_add_raw, fd6_to_double

	target = StatTarget.player()
	default_raw = stats.get_stat_default_value_fd6_raw(config, stat_type, nature)
	total_raw = default_raw
	for node, contribution_raw in stats.all_stat_contributions.items():
		if node.unique_stat.stat_type is not stat_type:
			continue
		if node.unique_stat.stat_nature is not nature:
			continue
		if not node.target.equals(target):
			continue
		total_raw = fd6_add_raw(total_raw, contribution_raw)
	return fd6_to_double(total_raw)


class ProfileMainBridge(QObject):
	changed = Signal()

	def __init__(
		self,
		player_getter: Callable[[], PlayerModel],
		parent: QObject | None = None,
	) -> None:
		super().__init__(parent)
		self._player_getter = player_getter
		self._ready = False
		self._weapon_title = ""
		self._weapon_subtitle = ""
		self._sub_stat_rows: list[dict[str, object]] = []
		self._combat_stat_rows: list[dict[str, object]] = []
		self._attack_speed_bonus_pct = 0.0
		self._attack_speed_multi = 1.0
		self._current_cycle_seconds = 0.0
		self._current_double_cycle_seconds = 0.0
		self._current_aps = 0.0
		self._breakpoint_rows: list[dict[str, object]] = []
		self._breakpoints_ready = False
		self._breakpoints_computing = False
		self.refresh()

	def refresh(self) -> None:
		player = self._player_getter()
		language = selected_language()
		stats = get_total_stats(player)
		config = player.game_config
		weapon_item = player.player_equipment_model.weapon
		item_id = weapon_item.item_id

		try:
			weapon = weapon_timing_from_library(
				weapon_idx=int(item_id.Idx),
				age=int(item_id.Age),
			)
		except KeyError:
			self._ready = False
			self._weapon_title = ""
			self._weapon_subtitle = "Weapon timing not found"
			self._sub_stat_rows = []
			self._combat_stat_rows = []
			self._clear_breakpoints()
			self.changed.emit()
			return

		attack_speed_multi = _resolved_player_stat_value(
			stats,
			config,
			StatType.AttackSpeed,
			StatNature.Multiplier,
		)
		metrics = analytic_cycle_metrics(weapon, attack_speed_multi=attack_speed_multi)
		self._ready = True
		self._weapon_title = self._weapon_title_text(weapon_item, language)
		self._weapon_subtitle = (
			f"Idx {item_id.Idx} · Age {int(item_id.Age)} · Lv {weapon_item.level} · "
			f"{'Ranged' if weapon.is_ranged else 'Melee'}"
		)
		self._sub_stat_rows = self._build_sub_stat_rows(stats, config, language)
		self._combat_stat_rows = self._build_combat_stat_rows(stats, config, language)
		self._attack_speed_bonus_pct = metrics.attack_speed_bonus_pct
		self._attack_speed_multi = metrics.attack_speed_multi
		self._current_cycle_seconds = metrics.game_tick_cycle_seconds
		self._current_double_cycle_seconds = metrics.double_cycle_seconds
		self._current_aps = metrics.game_tick_attacks_per_second
		self._clear_breakpoints()
		self.changed.emit()

	def _clear_breakpoints(self) -> None:
		self._breakpoint_rows = []
		self._breakpoints_ready = False
		self._breakpoints_computing = False

	@Slot()
	def computeBreakpoints(self) -> None:
		if not self._ready or self._breakpoints_computing:
			return
		player = self._player_getter()
		weapon_item = player.player_equipment_model.weapon
		item_id = weapon_item.item_id
		self._breakpoints_computing = True
		self.changed.emit()
		try:
			weapon = weapon_timing_from_library(
				weapon_idx=int(item_id.Idx),
				age=int(item_id.Age),
			)
			self._breakpoint_rows = self._build_breakpoint_rows(
				weapon,
				current_bonus_pct=self._attack_speed_bonus_pct,
			)
			self._breakpoints_ready = True
		except KeyError:
			self._clear_breakpoints()
		finally:
			self._breakpoints_computing = False
			self.changed.emit()

	def _weapon_title_text(self, weapon_item: ItemModel, language: str) -> str:
		key = _item_mapping_key(weapon_item.item_id)
		entry = ITEMS_MAPPING["items"].get(key)
		if entry is None:
			return f"Weapon {weapon_item.item_id.Idx}"
		name_loc_id, name_loc_table = name_loc_from_entry(entry)
		return get_localized(name_loc_id, table=name_loc_table, language=language)

	def _build_sub_stat_rows(
		self,
		stats,
		config,
		language: str,
	) -> list[dict[str, object]]:
		rows: list[dict[str, object]] = []
		balancing = config.item_balancing_config
		base_crit_bonus = (
			float(balancing.player_base_crit_damage)
			if balancing is not None
			else 0.0
		)
		for stat_type in SecondaryStatType:
			value = stats.total_secondary_stats.get(stat_type)
			if value is None or abs(float(value)) < 1e-9:
				continue
			display_value = _secondary_display_value(
				stat_type,
				float(value),
				base_crit_bonus,
			)
			if abs(display_value) < 1e-9:
				continue
			text = format_ui_secondary_stat_line(
				stat_type,
				display_value,
				game_config=config,
				language=language,
			)
			if not text:
				continue
			rows.append(_text_row(text, secondary=True))
		return rows

	def _build_combat_stat_rows(
		self,
		stats,
		config,
		language: str,
	) -> list[dict[str, object]]:
		rows: list[dict[str, object]] = []
		for stat_type in _PROFILE_COMBAT_STAT_TYPES:
			config_row = _stat_config_row(config, stat_type)
			if config_row is None:
				continue
			nature, _config_row = config_row
			value = _resolved_player_stat_value(stats, config, stat_type, nature)
			text = format_ui_resolved_stat_line(
				stat_type,
				value,
				nature,
				language=language,
			)
			if not text:
				continue
			rows.append(_text_row(text))
		return rows

	def _build_breakpoint_rows(
		self,
		weapon,
		*,
		current_bonus_pct: float,
	) -> list[dict[str, object]]:
		plateaus = attack_speed_breakpoint_rows(weapon)
		rows: list[dict[str, object]] = []
		for index, plateau in enumerate(plateaus):
			next_min = (
				plateaus[index + 1].min_bonus_pct
				if index + 1 < len(plateaus)
				else float("inf")
			)
			is_current = current_bonus_pct >= plateau.min_bonus_pct - 1e-9
			if next_min < float("inf"):
				is_current = is_current and current_bonus_pct < next_min - 1e-9
			rows.append(
				{
					"minBonusPct": plateau.min_bonus_pct,
					"attackSpeedMulti": plateau.attack_speed_multi,
					"cycleSeconds": plateau.cycle_seconds,
					"doubleCycleSeconds": plateau.double_cycle_seconds,
					"aps": plateau.aps,
					"doubleAps": plateau.double_aps,
					"isCurrent": is_current,
					"isReached": current_bonus_pct >= plateau.min_bonus_pct - 1e-9,
				}
			)
		return rows

	@Property(bool, notify=changed)
	def ready(self) -> bool:
		return self._ready

	@Property(str, notify=changed)
	def weaponTitle(self) -> str:
		return self._weapon_title

	@Property(str, notify=changed)
	def weaponSubtitle(self) -> str:
		return self._weapon_subtitle

	@Property("QVariantList", notify=changed)
	def subStatRows(self) -> list[dict[str, object]]:
		return self._sub_stat_rows

	@Property("QVariantList", notify=changed)
	def combatStatRows(self) -> list[dict[str, object]]:
		return self._combat_stat_rows

	@Property(float, notify=changed)
	def attackSpeedBonusPct(self) -> float:
		return self._attack_speed_bonus_pct

	@Property(float, notify=changed)
	def attackSpeedMulti(self) -> float:
		return self._attack_speed_multi

	@Property(float, notify=changed)
	def currentCycleSeconds(self) -> float:
		return self._current_cycle_seconds

	@Property(float, notify=changed)
	def currentDoubleCycleSeconds(self) -> float:
		return self._current_double_cycle_seconds

	@Property(float, notify=changed)
	def currentAps(self) -> float:
		return self._current_aps

	@Property("QVariantList", notify=changed)
	def breakpointRows(self) -> list[dict[str, object]]:
		return self._breakpoint_rows

	@Property(bool, notify=changed)
	def breakpointsReady(self) -> bool:
		return self._breakpoints_ready

	@Property(bool, notify=changed)
	def breakpointsComputing(self) -> bool:
		return self._breakpoints_computing
