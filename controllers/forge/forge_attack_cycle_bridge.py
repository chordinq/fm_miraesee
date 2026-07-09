from __future__ import annotations

from collections.abc import Callable

from PySide6.QtCore import Property, QObject, Signal

from config import ITEMS_MAPPING
from core.format.localizer_base import get_localized, selected_language
from core.format.number_format import format_percentage
from core.format.stats_format import format_stat_node
from core.game_logic.enums import StatNature, StatType
from core.game_logic.player.player_equipment_model import ItemId, ItemModel
from core.game_logic.player.player_model import PlayerModel, get_total_stats
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import StatTarget
from core.metaplaymath.fd6 import fd6_to_double
from ui.utils.localizer import name_loc_from_entry
from utils.combat.attack_cycle import analytic_cycle_metrics, game_tick_seconds, weapon_timing_from_library


def _item_mapping_key(item_id: ItemId) -> str:
	return f"{item_id.Age.value}_{item_id.Type.value}_{item_id.Idx}"


def _line(text: str, *, secondary: bool = False, heading: bool = False) -> dict[str, object]:
	return {"text": text, "secondary": secondary, "heading": heading}


def _seconds_text(value: float) -> str:
	return f"{value:.3f}s"


def _bpm_text(value: float) -> str:
	return f"{value:.2f} BPM"


class ForgeAttackCycleBridge(QObject):
	changed = Signal()

	def __init__(
		self,
		player_getter: Callable[[], PlayerModel],
		parent: QObject | None = None,
	) -> None:
		super().__init__(parent)
		self._player_getter = player_getter
		self._ready = False
		self._title_text = ""
		self._subtitle_text = ""
		self._footer_text = ""
		self._detail_lines: list[dict[str, object]] = []
		self.refresh()

	def refresh(self) -> None:
		player = self._player_getter()
		language = selected_language()
		weapon_item = player.player_equipment_model.weapon
		item_id = weapon_item.item_id

		try:
			weapon = weapon_timing_from_library(
				weapon_idx=int(item_id.Idx),
				age=int(item_id.Age),
			)
		except KeyError:
			self._ready = False
			self._title_text = "Attack cycle"
			self._subtitle_text = "Weapon timing not found in WeaponLibrary.json"
			self._footer_text = ""
			self._detail_lines = []
			self.changed.emit()
			return

		stats = get_total_stats(player)
		attack_speed_multi = StatHelper.calculate_value_from_stats(
			player.game_config,
			stats,
			StatType.AttackSpeed,
			StatTarget.player(),
			1.0,
		)
		metrics = analytic_cycle_metrics(weapon, attack_speed_multi=attack_speed_multi)
		self._ready = True
		self._title_text = self._weapon_title(weapon_item, language)
		self._subtitle_text = (
			f"Idx {item_id.Idx} · Age {int(item_id.Age)} · Lv {weapon_item.level} · "
			f"{'Ranged' if weapon.is_ranged else 'Melee'}"
		)
		self._detail_lines = self._build_detail_lines(
			player,
			stats,
			weapon,
			metrics,
			language,
		)
		self._footer_text = (
			f"IL 2.6.0: PlayerModel.GameTick uses F64.Ratio(1, 10) = {game_tick_seconds():.1f}s per tick. "
			"AttacksSystem.HandleUnits advances AttackTimer by tick × AttackSpeedMulti; "
			"windup ends at WindUpDuration, recovery ends at AttackDuration on the same timer. "
			"Double attack resets to 75% windup (4× speed-up constant)."
		)
		self.changed.emit()

	def _weapon_title(self, weapon_item: ItemModel, language: str) -> str:
		key = _item_mapping_key(weapon_item.item_id)
		entry = ITEMS_MAPPING["items"].get(key)
		if entry is None:
			return f"Weapon {weapon_item.item_id.Idx}"
		name_loc_id, name_loc_table = name_loc_from_entry(entry)
		name = get_localized(name_loc_id, table=name_loc_table, language=language)
		return name

	def _build_detail_lines(
		self,
		player: PlayerModel,
		stats,
		weapon,
		metrics,
		language: str,
	) -> list[dict[str, object]]:
		lines: list[dict[str, object]] = []

		lines.append(_line("Attack speed (total)", heading=True))
		lines.append(
			_line(
				f"Multiplier ×{metrics.attack_speed_multi:.4f} "
				f"({format_percentage(metrics.attack_speed_multi - 1.0)})",
			)
		)

		source_lines = self._attack_speed_source_lines(stats, language)
		if source_lines:
			lines.append(_line("Sources (equipment / pet / mount / …)", secondary=True))
			lines.extend(source_lines)
		else:
			lines.append(_line("No explicit AttackSpeed contributions in total stats.", secondary=True))

		lines.append(_line("Weapon base timing", heading=True))
		lines.append(_line(f"WindupTime (config): {_seconds_text(weapon.windup_time)}"))
		lines.append(_line(f"AttackDuration (config): {_seconds_text(weapon.attack_duration)}"))
		lines.append(_line(f"Recovery portion: {_seconds_text(weapon.recovery_time)}", secondary=True))
		lines.append(_line(f"Attack range: {weapon.attack_range:.2f}"))

		lines.append(_line("Resolved attack cycle", heading=True))
		lines.append(_line(f"Game tick (IL): {_seconds_text(game_tick_seconds())}", secondary=True))
		lines.append(_line(f"Windup @ current speed: {_seconds_text(metrics.windup_seconds)}"))
		lines.append(_line(f"Recovery @ current speed: {_seconds_text(metrics.recovery_seconds)}"))
		lines.append(
			_line(
				"Continuous (AttackDuration ÷ speed): "
				f"{_seconds_text(metrics.primary_cycle_seconds)} · "
				f"{metrics.primary_attacks_per_second:.3f}/s",
				secondary=True,
			)
		)
		lines.append(
			_line(
				"GameTick sim (0.1s steps): "
				f"{_seconds_text(metrics.game_tick_cycle_seconds)} · "
				f"{_bpm_text(metrics.game_tick_bpm)}"
			)
		)
		lines.append(
			_line(
				f"GameTick APS: {metrics.game_tick_attacks_per_second:.3f}/s",
				secondary=True,
			)
		)

		lines.append(_line("Double attack sequence", heading=True))
		lines.append(
			_line(
				f"Extra delay (25% windup ÷ speed): {_seconds_text(metrics.double_hit_delay_seconds)}"
			)
		)
		lines.append(
			_line(f"Double cycle (primary + delay): {_seconds_text(metrics.double_cycle_seconds)}")
		)
		lines.append(
			_line(f"Double sequence APS: {metrics.double_attacks_per_second:.3f}/s", secondary=True)
		)

		return lines

	def _attack_speed_source_lines(self, stats, language: str) -> list[dict[str, object]]:
		lines: list[dict[str, object]] = []
		for node, raw in stats.all_stat_contributions.items():
			if node.unique_stat.stat_type is not StatType.AttackSpeed:
				continue
			value = fd6_to_double(raw)
			if abs(value) < 1e-9:
				continue
			text = format_stat_node(
				node,
				value,
				show_multipliers_as_percentage=True,
				show_value_at_end=True,
				language=language,
			)
			if not text:
				continue
			nature = node.unique_stat.stat_nature
			lines.append(_line(text, secondary=nature is not StatNature.Multiplier))
		return lines

	@Property(bool, notify=changed)
	def ready(self) -> bool:
		return self._ready

	@Property(str, notify=changed)
	def titleText(self) -> str:
		return self._title_text

	@Property(str, notify=changed)
	def subtitleText(self) -> str:
		return self._subtitle_text

	@Property(str, notify=changed)
	def footerText(self) -> str:
		return self._footer_text

	@Property("QVariantList", notify=changed)
	def detailLines(self) -> list[dict[str, object]]:
		return self._detail_lines
