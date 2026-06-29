from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from config import MOUNTS_MAPPING, SPRITES_DIR
from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType, StatType
from core.game_logic.game_logic import GameLogic
from core.game_logic.stats.stat_helper import StatHelper
from controllers.collections.mount_collection_bridge import MountCollectionBridge
from controllers.support.summon_overdraft import can_afford_summon_for_ui, execute_mount_summon
from ui.utils.summon_result_entries import build_mount_summon_results
from ui.utils.ui_settings import register_display_refresh, register_economy_refresh


def _mount_key_from_model(mount) -> str:
    key = f"{mount.mount_id.rarity.value}_{mount.mount_id.id}"
    return MOUNTS_MAPPING[key]["Key"]


def _find_mount_by_guid(logic: GameLogic, mount_guid: str):
    for mount in logic.player.player_mount_collection_model.player_mount_models:
        if mount.guid == mount_guid:
            return mount
    return None


class MountSummonTestBridge(QObject):
    stateChanged = Signal()

    def __init__(
        self,
        logic: GameLogic,
        mount_collection: MountCollectionBridge | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._logic = logic
        self._mount_collection = mount_collection
        summon_config = logic.player.game_config.mount_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._status_text = ""
        self._last_action_text = ""
        self._summon_results: list[dict[str, object]] = []
        self._summon_sprite_image = QUrl.fromLocalFile(
            str(SPRITES_DIR / "Currency" / "clockWinders.png")
        ).toString()
        self._sync_status()
        self._refresh_prediction()
        register_display_refresh(self._on_ui_settings_changed)
        register_economy_refresh(self._on_ui_settings_changed)

    def _on_ui_settings_changed(self) -> None:
        self.stateChanged.emit()

    def reload_after_dump(self) -> None:
        summon_config = self._logic.player.game_config.mount_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._last_action_text = ""
        self._summon_results = []
        self._sync_status()
        self._refresh_prediction()
        self.stateChanged.emit()

    def _summon_config(self):
        return self._logic.player.game_config.mount_summon_config

    def _resolve_summon_cost(self, count: int) -> int:
        player = self._logic.player
        summon_config = self._summon_config()
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
        return list(self._summon_config().possible_summon_count)

    def _can_afford_count(self, count: int) -> bool:
        return can_afford_summon_for_ui(
            self._summon_config(),
            self._logic.player,
            count,
        )

    def _sync_status(self) -> None:
        player = self._logic.player
        collection = player.player_mount_collection_model
        summon = collection.summon_model
        clock_winders = player.player_currency_model.get(CurrencyType.ClockWinders)
        total_cost = self._resolve_summon_cost(self._summon_count)
        self._status_text = (
            f"clock winders {clock_winders}  cost {total_cost}  "
            f"seed {summon.seed:#018x}  lv {summon.level}  count {summon.count}"
        )

    def _refresh_prediction(self) -> None:
        self._summon_results = self._simulate_summon()

    def _refresh_collection(self) -> None:
        if self._mount_collection is not None:
            self._mount_collection.refresh()

    @Property(int, notify=stateChanged)
    def summonCount(self) -> int:
        return self._summon_count

    @Property(int, notify=stateChanged)
    def summonCost(self) -> int:
        return self._resolve_summon_cost(self._summon_count)

    @Property(int, notify=stateChanged)
    def clockWinderCount(self) -> int:
        return self._logic.player.player_currency_model.get(CurrencyType.ClockWinders)

    @Property(bool, notify=stateChanged)
    def canAffordSummon(self) -> bool:
        return self._can_afford_count(self._summon_count)

    @Property("QVariantList", notify=stateChanged)
    def summonAffordFlags(self) -> list[bool]:
        return [self._can_afford_count(count) for count in self._summon_count_options()]

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
    def lastActionText(self) -> str:
        return self._last_action_text

    @Property("QVariantList", notify=stateChanged)
    def summonResults(self) -> list[dict[str, object]]:
        return self._summon_results

    @Property(int, notify=stateChanged)
    def ascensionLevel(self) -> int:
        if self._mount_collection is None:
            return 0
        return self._mount_collection.ascensionLevel

    @Slot(int)
    def setSummonCount(self, count: int) -> None:
        if count not in self._summon_count_options():
            return
        if count == self._summon_count:
            return
        self._summon_count = count
        self._refresh_prediction()
        self._sync_status()
        self.stateChanged.emit()

    @Slot()
    def predictSummon(self) -> None:
        self._refresh_prediction()
        self._sync_status()
        self.stateChanged.emit()

    @Slot()
    def performSummon(self) -> None:
        count = self._summon_count
        result, summoned = execute_mount_summon(self._logic, count, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"summon failed: {result.name}"
        else:
            self._summon_results = build_mount_summon_results(
                summoned,
                self._logic.player,
            )
            parts = [f"summon x{count} ok"]
            for info in summoned:
                mount = info.mount_model
                detail = "NEW" if info.is_new else "duplicate"
                parts.append(
                    f"  {_mount_key_from_model(mount)}  {detail}"
                )
            self._last_action_text = "\n".join(parts)
        self._refresh_collection()
        self._sync_status()
        self._refresh_prediction()
        self.stateChanged.emit()

    @Slot(str)
    def performMountEquip(self, mount_guid: str) -> None:
        result = self._logic.mount_equip(mount_guid, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"equip failed: {result.name}"
        else:
            mount = _find_mount_by_guid(self._logic, mount_guid)
            name = _mount_key_from_model(mount) if mount is not None else mount_guid[:16]
            self._last_action_text = f"equipped {name}"
        self._refresh_collection()
        self._sync_status()
        self.stateChanged.emit()

    @Slot(str)
    def performMountUnequip(self, mount_guid: str) -> None:
        result = self._logic.mount_unequip(mount_guid, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"unequip failed: {result.name}"
        else:
            mount = _find_mount_by_guid(self._logic, mount_guid)
            name = _mount_key_from_model(mount) if mount is not None else mount_guid[:16]
            self._last_action_text = f"unequipped {name}"
        self._refresh_collection()
        self._sync_status()
        self.stateChanged.emit()

    def _simulate_summon(self) -> list[dict[str, object]]:
        player = copy.deepcopy(self._logic.player)
        logic = GameLogic(player)
        result, summoned = execute_mount_summon(logic, self._summon_count, commit=True)
        if result != ActionResult.Success:
            return []
        return build_mount_summon_results(summoned, player)
