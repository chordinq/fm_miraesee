from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from config import SKILLS_MAPPING, SPRITES_DIR
from core.game_logic.actions import ActionResult
from core.game_logic.actions.skill.skill_upgrade_action import SkillUpgradeAction
from core.game_logic.enums import CombatSkill, CurrencyType, StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id
from core.game_logic.stats.stat_helper import StatHelper
from ui.utils.guild_war_helper import (
    war_points_for_skill_summon,
    war_points_for_skill_upgrades,
)
from controllers.collections.skill_collection_bridge import SkillCollectionBridge
from controllers.summon.summon_upgrade_status import read_summon_upgrade_status
from controllers.support.summon_overdraft import can_afford_summon_for_ui, execute_skill_summon
from ui.utils.summon_result_entries import build_skill_summon_results
from ui.utils.ui_settings import register_display_refresh, register_economy_refresh


def _skill_key(combat_skill) -> str:
    skill_id = combat_skill_to_skill_id(combat_skill)
    return SKILLS_MAPPING[f"{skill_id.rarity.value}_{skill_id.idx}"]["Key"]


class SkillSummonTestBridge(QObject):
    stateChanged = Signal()
    statsRefreshRequested = Signal()

    def __init__(self, logic: GameLogic, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._logic = logic
        player = logic.player
        summon_config = player.game_config.skill_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._skill_collection = SkillCollectionBridge(
            player.player_skill_collection_model,
            player,
            parent=self,
        )
        self._prediction_text = ""
        self._status_text = ""
        self._last_action_text = ""
        self._summon_results: list[dict[str, object]] = []
        self._total_war_points = 0
        self._guild_war_day = 0
        self._summon_sprite_image = QUrl.fromLocalFile(
            str(SPRITES_DIR / "Currency" / "skillTicket.png")
        ).toString()
        self._war_points_sprite_image = QUrl.fromLocalFile(
            str(SPRITES_DIR / "Currency" / "Token.png")
        ).toString()
        self._sync_status()
        self._refresh_prediction()
        register_display_refresh(self._on_ui_settings_changed)
        register_economy_refresh(self._on_ui_settings_changed)

    def _on_ui_settings_changed(self) -> None:
        self.stateChanged.emit()

    def reload_from_player(self, player: PlayerModel, *, defer_heavy: bool = False) -> None:
        summon_config = player.game_config.skill_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._total_war_points = 0
        self._last_action_text = ""
        self._skill_collection.reload(
            player.player_skill_collection_model,
            player,
        )
        if defer_heavy:
            return
        self.finish_deferred_reload()

    def finish_deferred_reload(self) -> None:
        self._sync_status()
        self._refresh_prediction()
        self.stateChanged.emit()

    def _refresh_prediction(self) -> None:
        lines, _war_points, results = self._simulate_summon()
        self._prediction_text = "\n".join(lines)
        self._summon_results = results

    def _resolve_summon_cost(self, count: int) -> int:
        player = self._logic.player
        summon_config = player.game_config.skill_summon_config
        base_amount = summon_config.single_summon_cost.amount * count
        target = summon_config.summonable_id.get_stat_target()

        return round(
            StatHelper.calculate_value(
                player,
                StatType.Cost,
                target,
                base_amount,
            )
        )

    def _summon_count_options(self) -> list[int]:
        summon_config = self._logic.player.game_config.skill_summon_config
        return list(summon_config.possible_summon_count)

    def _can_afford_count(self, count: int) -> bool:
        return can_afford_summon_for_ui(
            self._logic.player.game_config.skill_summon_config,
            self._logic.player,
            count,
        )

    def _can_quick_upgrade(self) -> bool:
        result, _ = self._logic.skills_quick_upgrade(commit=False)
        return result == ActionResult.Success

    def _sync_status(self) -> None:
        player = self._logic.player
        collection = player.player_skill_collection_model
        summon = collection.summon_model
        tickets = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
        total_cost = self._resolve_summon_cost(self._summon_count)
        self._status_text = (
            f"tickets {tickets}  cost {total_cost}  "
            f"seed {summon.seed:#018x}  lv {summon.level}  count {summon.count}"
        )

    @Property(QObject, notify=stateChanged)
    def skillCollection(self) -> SkillCollectionBridge:
        return self._skill_collection

    @Property(int, notify=stateChanged)
    def summonCount(self) -> int:
        return self._summon_count

    @Property(int, notify=stateChanged)
    def summonCost(self) -> int:
        return self._resolve_summon_cost(self._summon_count)

    @Property(int, notify=stateChanged)
    def ticketCount(self) -> int:
        return self._logic.player.player_currency_model.get(CurrencyType.SkillSummonTickets)

    @Property(int, notify=stateChanged)
    def totalWarPoints(self) -> int:
        return self._total_war_points

    @Property(int, notify=stateChanged)
    def guildWarDay(self) -> int:
        return self._guild_war_day

    @Property(str, notify=stateChanged)
    def warPointsSpriteImage(self) -> str:
        return self._war_points_sprite_image

    @Property(bool, notify=stateChanged)
    def canAffordSummon(self) -> bool:
        return self._can_afford_count(self._summon_count)

    @Property(bool, notify=stateChanged)
    def canUpgradeAll(self) -> bool:
        return self._can_quick_upgrade()

    @Property("QVariantList", notify=stateChanged)
    def summonCountOptions(self) -> list[int]:
        return self._summon_count_options()

    @Property(str, notify=stateChanged)
    def summonSpriteImage(self) -> str:
        return self._summon_sprite_image

    @Property(str, notify=stateChanged)
    def statusText(self) -> str:
        return self._status_text

    @Property(str, notify=stateChanged)
    def predictionText(self) -> str:
        return self._prediction_text

    @Property(str, notify=stateChanged)
    def lastActionText(self) -> str:
        return self._last_action_text

    @Property("QVariantList", notify=stateChanged)
    def summonResults(self) -> list[dict[str, object]]:
        return self._summon_results

    @Property(int, notify=stateChanged)
    def ascensionLevel(self) -> int:
        return self._skill_collection.ascensionLevel

    def _summon_upgrade_status(self) -> dict[str, int | float | bool]:
        player = self._logic.player
        return read_summon_upgrade_status(
            player.player_skill_collection_model.summon_model,
            player.game_config.skill_summon_config,
        )

    @Property(int, notify=stateChanged)
    def summonLevel(self) -> int:
        return int(self._summon_upgrade_status()["summonLevel"])

    @Property(int, notify=stateChanged)
    def summonProgressCount(self) -> int:
        return int(self._summon_upgrade_status()["progressCount"])

    @Property(int, notify=stateChanged)
    def summonProgressRequired(self) -> int:
        return int(self._summon_upgrade_status()["progressRequired"])

    @Property(float, notify=stateChanged)
    def summonProgressFraction(self) -> float:
        return float(self._summon_upgrade_status()["progressFraction"])

    @Property(bool, notify=stateChanged)
    def summonProgressMaxed(self) -> bool:
        return bool(self._summon_upgrade_status()["isMaxed"])

    @Slot(int)
    def setSummonCount(self, count: int) -> None:
        if count not in self._summon_count_options():
            return
        if count == self._summon_count:
            return
        self._summon_count = count
        self._refresh_prediction()
        self.stateChanged.emit()

    @Slot()
    def predictSummon(self) -> None:
        self._refresh_prediction()
        self.stateChanged.emit()

    @Slot()
    def performSummon(self) -> None:
        count = self._summon_count
        result, summoned = execute_skill_summon(self._logic, count, commit=True)
        had_new = False
        if result != ActionResult.Success:
            self._last_action_text = f"summon failed: {result.name}"
        else:
            had_new = any(info.is_new for info in summoned)
            earned_war_points = war_points_for_skill_summon(self._guild_war_day, summoned)
            self._total_war_points += earned_war_points
            self._summon_results = build_skill_summon_results(
                summoned,
                self._logic.player,
            )
            parts = [f"summon x{count} ok (+{earned_war_points} war points, total {self._total_war_points})"]
            for info in summoned:
                skill = self._logic.player.player_skill_collection_model.try_get_skill(info.type)
                if skill is None:
                    continue
                if info.is_new:
                    parts.append(f"  NEW {_skill_key(info.type)} Lv{skill.level + 1}")
                else:
                    parts.append(
                        f"  {_skill_key(info.type)} shard+1 (total {skill.shard_count})"
                    )
            self._last_action_text = "\n".join(parts)
            self._skill_collection.patch_after_skill_summon(summoned)
        self._sync_status()
        self.predictSummon()
        self.stateChanged.emit()
        if had_new:
            self.statsRefreshRequested.emit()

    def _combat_skill_from_type(self, combat_skill_type: int) -> CombatSkill | None:
        try:
            return CombatSkill(combat_skill_type)
        except ValueError:
            return None

    def _resolve_equip_slot(self, combat_skill: CombatSkill) -> int:
        player = self._logic.player
        collection = player.player_skill_collection_model
        skill = collection.try_get_skill(combat_skill)
        if skill is not None and skill.is_equipped:
            return skill.equip_slot
        empty_slots = collection.get_empty_slots(player)
        if empty_slots:
            return empty_slots[0]
        return 0

    @Slot(int)
    def performSkillUpgrade(self, combat_skill_type: int) -> None:
        combat_skill = self._combat_skill_from_type(combat_skill_type)
        if combat_skill is None:
            return
        action = SkillUpgradeAction(combat_skill)
        result = action.execute(self._logic.player, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"upgrade failed: {result.name}"
        else:
            skill = self._logic.player.player_skill_collection_model.try_get_skill(combat_skill)
            level = skill.level + 1 if skill is not None else 0
            self._last_action_text = f"upgraded {_skill_key(combat_skill)} to Lv{level}"
        self._skill_collection.refresh()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot(int)
    def performSkillEquip(self, combat_skill_type: int) -> None:
        combat_skill = self._combat_skill_from_type(combat_skill_type)
        if combat_skill is None:
            return
        slot_id = self._resolve_equip_slot(combat_skill)
        result = self._logic.skill_equip(combat_skill, slot_id, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"equip failed: {result.name}"
        else:
            self._last_action_text = f"equipped {_skill_key(combat_skill)} slot {slot_id + 1}"
        self._skill_collection.refresh()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot(int)
    def performSkillUnequip(self, combat_skill_type: int) -> None:
        combat_skill = self._combat_skill_from_type(combat_skill_type)
        if combat_skill is None:
            return
        result = self._logic.skill_unequip(combat_skill, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"unequip failed: {result.name}"
        else:
            self._last_action_text = f"unequipped {_skill_key(combat_skill)}"
        self._skill_collection.refresh()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot()
    def performUpgradeAll(self) -> None:
        result, upgraded = self._logic.skills_quick_upgrade(commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"upgrade all failed: {result.name}"
        else:
            earned_war_points = war_points_for_skill_upgrades(
                self._guild_war_day,
                upgraded,
            )
            self._total_war_points += earned_war_points
            self._last_action_text = (
                f"upgrade all ok (+{len(upgraded)} levels, "
                f"+{earned_war_points} war points, total {self._total_war_points})"
            )
        self._skill_collection.refresh()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot()
    def performQuickEquip(self) -> None:
        result = self._logic.skills_quick_equip(commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"quick equip failed: {result.name}"
        else:
            self._last_action_text = "quick equip ok"
        self._skill_collection.refresh()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    def _simulate_summon(self) -> tuple[list[str], int, list[dict[str, object]]]:
        player = copy.deepcopy(self._logic.player)
        logic = GameLogic(player)
        collection = player.player_skill_collection_model
        summon = collection.summon_model
        tickets_before = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
        seed_before = summon.seed
        level_before = summon.level
        count_before = summon.count

        result, summoned = execute_skill_summon(logic, self._summon_count, commit=True)
        if result != ActionResult.Success:
            return [f"predict unavailable: {result.name}"], 0, []

        war_points = war_points_for_skill_summon(self._guild_war_day, summoned)
        results = build_skill_summon_results(summoned, player)

        lines = [
            f"next x{self._summon_count} (simulated, state unchanged)",
            "",
        ]
        for index, info in enumerate(summoned, 1):
            skill = collection.try_get_skill(info.type)
            if skill is None:
                continue
            if info.is_new:
                detail = "NEW"
            else:
                detail = f"shard+1 -> {skill.shard_count}"
            lines.append(
                f"{index:>2}. {_skill_key(info.type)}  Lv{skill.level + 1}  {detail}"
            )

        tickets_after = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
        lines.extend(
            [
                "",
                f"war points +{war_points}",
                f"seed  {seed_before:#018x} -> {summon.seed:#018x}",
                f"meta  lv {level_before} -> {summon.level}  count {count_before} -> {summon.count}",
                f"tickets {tickets_before} -> {tickets_after}",
            ]
        )
        return lines, war_points, results
