from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot

from config import PETS_MAPPING, SPRITES_DIR
from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType, StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.stats.stat_helper import StatHelper
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.summon.summon_upgrade_status import read_summon_upgrade_status
from controllers.support.summon_overdraft import can_afford_summon_for_ui, execute_egg_summon
from ui.utils.summon_preview_entries import build_egg_summon_preview
from ui.utils.summon_result_summary import build_summon_result_summary
from ui.utils.ui_settings import register_display_refresh, register_economy_refresh
from utils.summon.bonus_optimizer import optimize_egg_summon_bonus


def _pet_key_from_model(pet) -> str:
    key = f"{pet.pet_id.rarity.value}_{pet.pet_id.id}"
    return PETS_MAPPING[key]["Key"]


def _find_pet_by_guid(logic: GameLogic, pet_guid: str):
    for pet in logic.player.player_pet_collection_model.pets:
        if pet.guid == pet_guid:
            return pet
    return None


class PetSummonTestBridge(QObject):
    stateChanged = Signal()
    statsRefreshRequested = Signal()

    def __init__(
        self,
        logic: GameLogic,
        pet_collection: PetCollectionBridge | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._logic = logic
        self._pet_collection = pet_collection
        summon_config = logic.player.game_config.egg_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._prediction_text = ""
        self._status_text = ""
        self._last_action_text = ""
        self._summon_preview: list[dict[str, object]] = []
        self._summon_result: dict[str, object] = build_summon_result_summary([], 0)
        self._merge_target_guid = ""
        self._prediction_timer = QTimer(self)
        self._prediction_timer.setSingleShot(True)
        self._prediction_timer.timeout.connect(self._on_deferred_prediction_refresh)
        self._summon_sprite_image = QUrl.fromLocalFile(
            str(SPRITES_DIR / "Currency" / "Eggshells.png")
        ).toString()
        self._optimize_budget: int = 30
        self._optimize_route: str = ""
        self._optimize_route_segments: list[str] = []
        self._optimize_bonus: int = 0
        self._optimize_total: int = 0
        self._optimize_ready: bool = False
        self._is_optimizing: bool = False
        self._sync_status()
        self._refresh_prediction()
        register_display_refresh(self._on_ui_settings_changed)
        register_economy_refresh(self._on_ui_settings_changed)

    def _on_ui_settings_changed(self) -> None:
        self.stateChanged.emit()

    def reload_after_dump(self, *, defer_heavy: bool = False) -> None:
        summon_config = self._logic.player.game_config.egg_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._last_action_text = ""
        self._summon_preview = []
        self._summon_result = build_summon_result_summary([], 0)
        self._merge_target_guid = ""
        self._optimize_route = ""
        self._optimize_route_segments = []
        self._optimize_bonus = 0
        self._optimize_total = 0
        self._optimize_ready = False
        self._is_optimizing = False
        if defer_heavy:
            return
        self.finish_deferred_reload()

    def finish_deferred_reload(self) -> None:
        self._sync_status()
        self._refresh_prediction()
        self.stateChanged.emit()

    def _summon_config(self):
        return self._logic.player.game_config.egg_summon_config

    def _resolve_summon_cost(self, count: int) -> int:
        player = self._logic.player
        summon_config = self._summon_config()
        base_amount = summon_config.single_summon_cost.amount * count
        target = summon_config.summonable_id.get_stat_target()
        return StatHelper.calculate_value_round_to_int(
            player,
            StatType.Cost,
            target,
            base_amount,
        )

    def _summon_count_options(self) -> list[int]:
        return list(self._summon_config().possible_summon_count)

    def _can_afford_count(self, count: int) -> bool:
        return can_afford_summon_for_ui(
            self._summon_config(),
            self._logic.player,
            count,
        )

    def _sync_status(self) -> None:
        player = self._logic.player
        collection = player.player_pet_collection_model
        summon = collection.summon_model
        shells = player.player_currency_model.get(CurrencyType.Eggshells)
        total_cost = self._resolve_summon_cost(self._summon_count)
        self._status_text = (
            f"eggshells {shells}  cost {total_cost}  "
            f"seed {summon.seed:#018x}  lv {summon.level}  count {summon.count}"
        )

    def _refresh_prediction(self) -> None:
        lines, results = self._simulate_summon()
        self._prediction_text = "\n".join(lines)
        self._summon_preview = results
        self._summon_result = build_summon_result_summary(results, self._summon_count)

    def _set_summon_preview(
        self,
        preview: list[dict[str, object]],
        paid_count: int,
    ) -> None:
        self._summon_preview = preview
        self._summon_result = build_summon_result_summary(preview, paid_count)

    def _schedule_prediction_refresh(self) -> None:
        self._prediction_timer.start(0)

    def _on_deferred_prediction_refresh(self) -> None:
        self._refresh_prediction()
        self.stateChanged.emit()

    def _finish_summon_collection_update(self, summoned) -> None:
        self._patch_egg_summon_collection(summoned)
        self.stateChanged.emit()
        self._schedule_prediction_refresh()

    @Property(int, notify=stateChanged)
    def summonCount(self) -> int:
        return self._summon_count

    @Property(int, notify=stateChanged)
    def summonCost(self) -> int:
        return self._resolve_summon_cost(self._summon_count)

    @Property(int, notify=stateChanged)
    def eggshellCount(self) -> int:
        return self._logic.player.player_currency_model.get(CurrencyType.Eggshells)

    @Property(bool, notify=stateChanged)
    def canAffordSummon(self) -> bool:
        return self._can_afford_count(self._summon_count)

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
    def summonPreview(self) -> list[dict[str, object]]:
        return self._summon_preview

    @Property("QVariantMap", notify=stateChanged)
    def summonResult(self) -> dict[str, object]:
        return self._summon_result

    @Property(int, notify=stateChanged)
    def ascensionLevel(self) -> int:
        if self._pet_collection is None:
            return 0
        return self._pet_collection.ascensionLevel

    def _summon_upgrade_status(self) -> dict[str, int | float | bool]:
        player = self._logic.player
        return read_summon_upgrade_status(
            player.player_pet_collection_model.summon_model,
            self._summon_config(),
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
        self._schedule_prediction_refresh()
        self._sync_status()
        self.stateChanged.emit()

    @Slot()
    def predictSummon(self) -> None:
        self._refresh_prediction()
        self._sync_status()
        self.stateChanged.emit()

    def _refresh_collection(self) -> None:
        if self._pet_collection is not None:
            self._pet_collection.refresh()

    def _patch_egg_summon_collection(self, summoned) -> None:
        if self._pet_collection is not None and summoned:
            self._pet_collection.patch_after_egg_summon(summoned)

    def _resolve_equip_slot(self, pet_guid: str) -> int:
        player = self._logic.player
        collection = player.player_pet_collection_model
        pet = _find_pet_by_guid(self._logic, pet_guid)
        if pet is not None and pet.is_equipped:
            return pet.equip_slot
        empty_slots = collection.get_empty_pet_slots(player)
        if empty_slots:
            return empty_slots[0]
        return 0

    @Property(str, notify=stateChanged)
    def mergeTargetGuid(self) -> str:
        return self._merge_target_guid

    @Slot(str)
    def beginPetMerge(self, pet_guid: str) -> None:
        self._merge_target_guid = pet_guid
        self.stateChanged.emit()

    @Slot()
    def clearPetMerge(self) -> None:
        self._merge_target_guid = ""
        self.stateChanged.emit()

    @Slot(str, result="QVariantList")
    def mergeCandidatesFor(self, target_guid: str) -> list[dict[str, object]]:
        collection = self._logic.player.player_pet_collection_model
        entries: list[dict[str, object]] = []
        for pet in collection.pets:
            if pet.guid == target_guid or pet.is_equipped:
                continue
            entries.append(
                {
                    "kind": "pet",
                    "guid": pet.guid,
                    "label": f"{_pet_key_from_model(pet)} Lv{pet.level}",
                    "rarity": pet.pet_id.rarity.value,
                    "index": pet.pet_id.id,
                }
            )
        for egg in collection.eggs:
            if egg.is_equipped:
                continue
            entries.append(
                {
                    "kind": "egg",
                    "guid": egg.guid,
                    "label": f"{egg.rarity.name} egg",
                    "rarity": egg.rarity.value,
                    "index": -1,
                }
            )
        return entries

    @Slot(str)
    def performPetEquip(self, pet_guid: str) -> None:
        slot = self._resolve_equip_slot(pet_guid)
        collection = self._logic.player.player_pet_collection_model
        displaced_guid: str | None = None
        for pet in collection.pets:
            if pet.is_equipped and pet.equip_slot == slot and pet.guid != pet_guid:
                displaced_guid = pet.guid
                break
        result = self._logic.pet_equip(pet_guid, slot, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"equip failed: {result.name}"
        else:
            pet = _find_pet_by_guid(self._logic, pet_guid)
            name = _pet_key_from_model(pet) if pet is not None else pet_guid[:16]
            self._last_action_text = f"equipped {name} slot {slot + 1}"
        if self._pet_collection is not None:
            self._pet_collection.patch_pet_equip_layout(pet_guid, displaced_guid)
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot(str)
    def performPetUnequip(self, pet_guid: str) -> None:
        result = self._logic.pet_unequip(pet_guid, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"unequip failed: {result.name}"
        else:
            pet = _find_pet_by_guid(self._logic, pet_guid)
            name = _pet_key_from_model(pet) if pet is not None else pet_guid[:16]
            self._last_action_text = f"unequipped {name}"
        if self._pet_collection is not None:
            self._pet_collection.patch_pet_equip_layout(pet_guid)
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot(str)
    def performPetToggleLock(self, pet_guid: str) -> None:
        pet = _find_pet_by_guid(self._logic, pet_guid)
        if pet is None:
            self._last_action_text = "lock toggle failed: pet not found"
            self.stateChanged.emit()
            return
        pet.is_locked = not pet.is_locked
        name = _pet_key_from_model(pet)
        state = "locked" if pet.is_locked else "unlocked"
        self._last_action_text = f"{state} {name}"
        if self._pet_collection is not None:
            self._pet_collection.patch_pet_lock(pet_guid)
        self._sync_status()
        self.stateChanged.emit()

    @Slot(str, "QVariantList", "QVariantList")
    def performPetMerge(
        self,
        target_guid: str,
        pet_source_guids: list[str],
        egg_source_guids: list[str],
    ) -> None:
        if not pet_source_guids and not egg_source_guids:
            self._last_action_text = "merge failed: no sources selected"
            self.stateChanged.emit()
            return

        target = _find_pet_by_guid(self._logic, target_guid)
        target_level = target.level if target is not None else 0
        result = self._logic.pet_merge(
            target_guid,
            list(pet_source_guids),
            list(egg_source_guids),
            commit=True,
        )
        if result != ActionResult.Success:
            self._last_action_text = f"merge failed: {result.name}"
        else:
            merged = _find_pet_by_guid(self._logic, target_guid)
            new_level = merged.level if merged is not None else target_level
            source_count = len(pet_source_guids) + len(egg_source_guids)
            name = _pet_key_from_model(merged) if merged is not None else target_guid[:16]
            self._last_action_text = (
                f"merged {source_count} into {name} "
                f"(Lv{target_level} -> Lv{new_level})"
            )
        self._merge_target_guid = ""
        self._refresh_collection()
        self._sync_status()
        self.statsRefreshRequested.emit()
        self.stateChanged.emit()

    @Slot()
    def performSummon(self) -> None:
        count = self._summon_count
        result, summoned = execute_egg_summon(self._logic, count, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"summon failed: {result.name}"
        else:
            self._set_summon_preview(
                build_egg_summon_preview(
                    summoned,
                    self._logic.player,
                ),
                count,
            )
            parts = [f"summon x{count} ok"]
            for info in summoned:
                egg = info.egg_model
                detail = "NEW" if info.is_new else "duplicate"
                parts.append(
                    f"  [{egg.rarity.name}] seed {egg.random_seed:#018x}  {detail}"
                )
            self._last_action_text = "\n".join(parts)
        self._sync_status()
        self.stateChanged.emit()
        if result == ActionResult.Success:
            QTimer.singleShot(0, lambda s=summoned: self._finish_summon_collection_update(s))
        else:
            self._schedule_prediction_refresh()

    @Property(int, notify=stateChanged)
    def optimizeBudget(self) -> int:
        return self._optimize_budget

    @Property(str, notify=stateChanged)
    def optimizeRoute(self) -> str:
        return self._optimize_route

    @Property("QVariantList", notify=stateChanged)
    def optimizeRouteSegments(self) -> list[str]:
        return self._optimize_route_segments

    @Property(int, notify=stateChanged)
    def optimizeBonus(self) -> int:
        return self._optimize_bonus

    @Property(int, notify=stateChanged)
    def optimizeTotal(self) -> int:
        return self._optimize_total

    @Property(bool, notify=stateChanged)
    def optimizeReady(self) -> bool:
        return self._optimize_ready

    @Property(bool, notify=stateChanged)
    def isOptimizing(self) -> bool:
        return self._is_optimizing

    @Slot(int)
    def setOptimizeBudget(self, budget: int) -> None:
        clamped = max(1, min(budget, 9999))
        if clamped == self._optimize_budget:
            return
        self._optimize_budget = clamped
        self._optimize_ready = False
        self.stateChanged.emit()

    @Slot()
    def runOptimize(self) -> None:
        self._is_optimizing = True
        self._optimize_ready = False
        self.stateChanged.emit()
        QTimer.singleShot(0, self._do_optimize)

    def _do_optimize(self) -> None:
        result = optimize_egg_summon_bonus(self._logic, self._optimize_budget)
        self._optimize_route = result.route_str
        self._optimize_route_segments = list(result.route_segments)
        self._optimize_bonus = result.best_bonus_count
        self._optimize_total = result.best_total_pulls
        self._optimize_ready = True
        self._is_optimizing = False
        self.stateChanged.emit()

    def _simulate_summon(self) -> tuple[list[str], list[dict[str, object]]]:
        player = copy.deepcopy(self._logic.player)
        logic = GameLogic(player)
        collection = player.player_pet_collection_model
        summon = collection.summon_model
        shells_before = player.player_currency_model.get(CurrencyType.Eggshells)
        seed_before = summon.seed
        level_before = summon.level
        count_before = summon.count

        result, summoned = execute_egg_summon(logic, self._summon_count, commit=True)
        if result != ActionResult.Success:
            return [f"predict unavailable: {result.name}"], []

        results = build_egg_summon_preview(summoned, player)

        lines = [
            f"next x{self._summon_count} (simulated, state unchanged)",
            "",
        ]
        for index, info in enumerate(summoned, 1):
            egg = info.egg_model
            detail = "NEW" if info.is_new else "duplicate"
            lines.append(
                f"{index:>2}. [{egg.rarity.name}]  seed {egg.random_seed:#018x}  {detail}"
            )

        shells_after = player.player_currency_model.get(CurrencyType.Eggshells)
        lines.extend(
            [
                "",
                f"seed  {seed_before:#018x} -> {summon.seed:#018x}",
                f"meta  lv {level_before} -> {summon.level}  count {count_before} -> {summon.count}",
                f"eggshells {shells_before} -> {shells_after}",
            ]
        )
        return lines, results
