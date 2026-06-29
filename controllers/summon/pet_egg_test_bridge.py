from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, Signal, Slot

from config import PETS_MAPPING
from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType, GemSkipTarget
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_currency_model import can_afford
from core.game_logic.player.player_pet_collection_model import PlayerEggModel
from ui.utils.egg_hatch_preview import build_egg_hatch_preview, format_hatch_duration
from ui.utils.number_display_format import format_ui_integer
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.common.timer_bar_bridge import TimerBarBridge


def _pet_key(pet_id) -> str:
    return PETS_MAPPING[f"{pet_id.rarity.value}_{pet_id.id}"]["Key"]


def _find_egg_by_guid(eggs: list[PlayerEggModel], egg_guid: str) -> PlayerEggModel | None:
    for egg in eggs:
        if egg.guid == egg_guid:
            return egg
    return None


class PetEggTestBridge(QObject):
    stateChanged = Signal()

    def __init__(
        self,
        logic: GameLogic,
        pet_collection: PetCollectionBridge | None = None,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._logic = logic
        self._pet_collection = pet_collection
        self._selected_egg_guid = ""
        self._prediction_text = ""
        self._predicted_pet_index = -1
        self._predicted_pet_rarity = -1
        self._stat_lines: list[dict[str, object]] = []
        self._hatch_desc_format_args: list[str] = []
        self._hatch_remaining_text = ""
        self._timer_bar_bridge = TimerBarBridge(self)
        self._timer_bar_bridge.displayChanged.connect(self.stateChanged.emit)
        self._ui_language = "en"
        self._status_text = self._build_status_text()
        self._last_action_text = ""

    def reload_after_dump(self) -> None:
        self._selected_egg_guid = ""
        self._clear_egg_preview()
        self._last_action_text = ""
        self._status_text = self._build_status_text()
        self.stateChanged.emit()

    def _collection(self):
        return self._logic.player.player_pet_collection_model

    def _build_status_text(self) -> str:
        collection = self._collection()
        inventory_eggs = sum(1 for egg in collection.eggs if not egg.is_equipped)
        hatching_eggs = sum(1 for egg in collection.eggs if egg.is_equipped)
        return (
            f"eggs {len(collection.eggs)}  inventory {inventory_eggs}  "
            f"hatching {hatching_eggs}  hatch slots {collection.unlocked_hatch_slots_count}"
        )

    def _selected_egg(self) -> PlayerEggModel | None:
        if not self._selected_egg_guid:
            return None
        return _find_egg_by_guid(self._collection().eggs, self._selected_egg_guid)

    def _first_available_hatch_slot(self) -> int | None:
        collection = self._collection()
        for slot in range(collection.unlocked_hatch_slots_count):
            if collection.is_hatch_slot_available(slot):
                return slot
        return None

    def _clear_egg_preview(self) -> None:
        self._prediction_text = ""
        self._predicted_pet_index = -1
        self._predicted_pet_rarity = -1
        self._stat_lines = []
        self._hatch_desc_format_args = []
        self._hatch_remaining_text = ""
        self._timer_bar_bridge.clear()

    def _sync_timer_bar_bridge(self) -> None:
        egg = self._selected_egg()
        if (
            egg is not None
            and egg.is_equipped
            and egg.timer is not None
            and egg.timer.end_time > egg.timer.start_time
        ):
            self._timer_bar_bridge.bind(
                egg.timer,
                self._logic.player,
                language=self._ui_language,
            )
            if egg.timer.has_ended(self._logic.player):
                self._hatch_remaining_text = ""
            else:
                self._hatch_remaining_text = self._timer_bar_bridge.remainingText
        else:
            self._timer_bar_bridge.clear()
            self._hatch_remaining_text = ""

    def _rebuild_egg_preview(self, egg_guid: str) -> None:
        source_egg = _find_egg_by_guid(self._collection().eggs, egg_guid)
        if source_egg is None:
            self._clear_egg_preview()
            return

        preview = build_egg_hatch_preview(
            self._logic.player,
            source_egg,
            language=self._ui_language,
        )
        self._predicted_pet_index = int(preview["predictedPetIndex"])
        self._predicted_pet_rarity = int(preview["predictedPetRarity"])
        self._stat_lines = list(preview["statLines"])
        self._hatch_desc_format_args = list(preview["hatchDescFormatArgs"])
        self._prediction_text = "\n".join(self._build_hatch_prediction_lines(egg_guid))
        self._sync_timer_bar_bridge()

    def _refresh_after_action(self, *, clear_selection: bool = False) -> None:
        if clear_selection:
            self._selected_egg_guid = ""
            self._clear_egg_preview()
        elif self._selected_egg_guid:
            self._rebuild_egg_preview(self._selected_egg_guid)
        if self._pet_collection is not None:
            self._pet_collection.refresh()
        self._status_text = self._build_status_text()
        self.stateChanged.emit()

    def refreshDisplayFormat(self) -> None:
        if self._selected_egg_guid:
            self._rebuild_egg_preview(self._selected_egg_guid)
        self.stateChanged.emit()

    @Property(str, notify=stateChanged)
    def statusText(self) -> str:
        return self._status_text

    @Property(str, notify=stateChanged)
    def predictionText(self) -> str:
        return self._prediction_text

    @Property(str, notify=stateChanged)
    def lastActionText(self) -> str:
        return self._last_action_text

    @Property(str, notify=stateChanged)
    def selectedEggGuid(self) -> str:
        return self._selected_egg_guid

    @Property(int, notify=stateChanged)
    def predictedPetIndex(self) -> int:
        return self._predicted_pet_index

    @Property(int, notify=stateChanged)
    def predictedPetRarity(self) -> int:
        return self._predicted_pet_rarity

    @Property("QVariantList", notify=stateChanged)
    def statLines(self) -> list[dict[str, object]]:
        return self._stat_lines

    @Property("QVariantList", notify=stateChanged)
    def hatchDescFormatArgs(self) -> list[str]:
        return self._hatch_desc_format_args

    @Property(QObject, constant=True)
    def selectedEggTimerBridge(self) -> TimerBarBridge:
        return self._timer_bar_bridge

    @Property(str, notify=stateChanged)
    def hatchRemainingText(self) -> str:
        return self._hatch_remaining_text

    @Slot(str)
    def setUiLanguage(self, language: str) -> None:
        if language == self._ui_language:
            return
        self._ui_language = language
        self._timer_bar_bridge.set_ui_language(language)
        if self._selected_egg_guid:
            self._rebuild_egg_preview(self._selected_egg_guid)
        self.stateChanged.emit()

    @Property(bool, notify=stateChanged)
    def hatchSlotsFull(self) -> bool:
        egg = self._selected_egg()
        if egg is None or egg.is_equipped:
            return False
        return self._first_available_hatch_slot() is None

    @Property(bool, notify=stateChanged)
    def hatchButtonEnabled(self) -> bool:
        return self.canStartHatch or self.canCompleteHatch

    @Property(bool, notify=stateChanged)
    def gemSkipVisible(self) -> bool:
        egg = self._selected_egg()
        if egg is None or not egg.is_equipped or egg.timer is None:
            return False
        if egg.timer.end_time <= egg.timer.start_time:
            return False
        return not egg.timer.has_ended(self._logic.player)

    @Property(str, notify=stateChanged)
    def skipGemCostText(self) -> str:
        egg = self._selected_egg()
        if egg is None or egg.timer is None:
            return ""
        if egg.timer.end_time <= egg.timer.start_time:
            return ""
        if egg.timer.has_ended(self._logic.player):
            return ""
        gem_cost = egg.timer.calculate_gem_skip_cost(
            self._logic.player,
            GemSkipTarget.PetEgg,
        )
        return format_ui_integer(gem_cost)

    @Property(bool, notify=stateChanged)
    def selectedEggHatching(self) -> bool:
        egg = self._selected_egg()
        if egg is None or egg.timer is None:
            return False
        return not egg.timer.has_ended(self._logic.player)

    @Property(bool, notify=stateChanged)
    def canStartHatch(self) -> bool:
        egg = self._selected_egg()
        if egg is None or egg.is_equipped or egg.timer is not None:
            return False
        return self._first_available_hatch_slot() is not None

    @Property(bool, notify=stateChanged)
    def canCompleteHatch(self) -> bool:
        egg = self._selected_egg()
        if egg is None:
            return False
        if not egg.is_equipped:
            return self._first_available_hatch_slot() is not None
        if egg.timer is None:
            return True
        return egg.timer.has_ended(self._logic.player)

    @Property(bool, notify=stateChanged)
    def canGemSkipHatch(self) -> bool:
        egg = self._selected_egg()
        if egg is None or egg.timer is None:
            return False
        if egg.timer.has_ended(self._logic.player):
            return False
        gem_cost = egg.timer.calculate_gem_skip_cost(
            self._logic.player,
            GemSkipTarget.PetEgg,
        )
        affordable, _ = can_afford(self._logic.player, CurrencyType.Gems, gem_cost)
        return affordable

    @Property(bool, notify=stateChanged)
    def canHatchSelected(self) -> bool:
        return self.canCompleteHatch

    @Property(float, notify=stateChanged)
    def hatchProgress(self) -> float:
        return self._timer_bar_bridge.progressFraction

    @Property(int, notify=stateChanged)
    def hatchRemainingSeconds(self) -> int:
        return self._timer_bar_bridge.remainingSeconds

    @Slot(str)
    def selectEgg(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        self._rebuild_egg_preview(egg_guid)
        self._status_text = self._build_status_text()
        self.stateChanged.emit()

    @Slot()
    def refreshSelectedEgg(self) -> None:
        if not self._selected_egg_guid:
            return
        if _find_egg_by_guid(self._collection().eggs, self._selected_egg_guid) is None:
            self._selected_egg_guid = ""
            self._clear_egg_preview()
        else:
            self._sync_timer_bar_bridge()
        self.stateChanged.emit()

    @Slot(str)
    def predictHatch(self, egg_guid: str) -> None:
        self.selectEgg(egg_guid)

    @Slot(str)
    def performStartHatch(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        slot = self._first_available_hatch_slot()
        if slot is None:
            self._last_action_text = "no hatch slot available"
            self.stateChanged.emit()
            return

        result = self._logic.pet_egg_hatch_start(egg_guid, slot, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"start hatch failed: {result.name}"
        else:
            self._last_action_text = f"started hatch in slot {slot + 1}"
        self._refresh_after_action()

    @Slot(str)
    def performCompleteHatch(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        egg = self._selected_egg()
        if egg is None:
            self._last_action_text = "egg not found"
            self.stateChanged.emit()
            return

        if not egg.is_equipped:
            slot = self._first_available_hatch_slot()
            if slot is None:
                self._last_action_text = "no hatch slot available"
                self.stateChanged.emit()
                return
            result, hatched = self._logic.pet_egg_hatch_complete(egg_guid, slot, commit=True)
        elif egg.timer is not None and not egg.timer.has_ended(self._logic.player):
            self._last_action_text = "hatch not ready"
            self.stateChanged.emit()
            return
        elif egg.timer is not None:
            claim_result = self._logic.pet_egg_hatch_claim(egg_guid, commit=True)
            if claim_result != ActionResult.Success:
                self._last_action_text = f"claim failed: {claim_result.name}"
                self.stateChanged.emit()
                return
            result, hatched = self._logic.pet_egg_hatch_finalize(egg_guid, commit=True)
        else:
            result, hatched = self._logic.pet_egg_hatch_finalize(egg_guid, commit=True)

        if result != ActionResult.Success or hatched is None:
            self._last_action_text = f"hatch failed: {result.name}"
        else:
            detail = "NEW" if hatched.is_new else "duplicate"
            self._last_action_text = (
                f"hatched {_pet_key(hatched.pet_id)} "
                f"(rarity {hatched.pet_id.rarity.value}, id {hatched.pet_id.id}, {detail})"
            )
        self._refresh_after_action(clear_selection=True)

    @Slot(str)
    def performGemSkipHatch(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        result = self._logic.pet_egg_hatch_gem_skip(egg_guid, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"gem skip failed: {result.name}"
        else:
            self._last_action_text = "timer skipped"
        self._refresh_after_action()

    @Slot()
    def performSelectedHatch(self) -> None:
        if not self._selected_egg_guid:
            self._last_action_text = "no egg selected"
            self.stateChanged.emit()
            return
        self.performHatch(self._selected_egg_guid)

    @Slot(str)
    def performHatch(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        egg = self._selected_egg()
        if egg is None:
            self._last_action_text = "egg not found"
            self.stateChanged.emit()
            return
        if self.canStartHatch:
            self.performStartHatch(egg_guid)
            return
        if self.canCompleteHatch:
            self.performCompleteHatch(egg_guid)
            return
        self._last_action_text = "hatch unavailable"
        self.stateChanged.emit()

    def _build_hatch_prediction_lines(self, egg_guid: str) -> list[str]:
        source_egg = _find_egg_by_guid(self._collection().eggs, egg_guid)
        if source_egg is None:
            return [f"egg not found: {egg_guid[:16]}"]

        player = copy.deepcopy(self._logic.player)
        logic = GameLogic(player)
        egg = _find_egg_by_guid(player.player_pet_collection_model.eggs, egg_guid)
        if egg is None:
            return [f"egg not found: {egg_guid[:16]}"]

        result, hatched = logic.pet_egg_hatch_finalize(egg_guid, commit=True)
        if result != ActionResult.Success or hatched is None:
            return [f"hatch preview unavailable: {result.name}"]

        location = "hatch slot" if source_egg.is_equipped else "inventory"
        slot_note = (
            f"slot {source_egg.equip_slot + 1}"
            if source_egg.is_equipped
            else "not in hatch slot"
        )
        detail = "NEW" if hatched.is_new else "duplicate"
        lines = [
            "hatch preview (simulated, state unchanged)",
            "",
            f"egg  {location} ({slot_note})",
            f"     rarity {source_egg.rarity.value}  seed {source_egg.seed:#018x}",
            "",
            f"pet  {_pet_key(hatched.pet_id)}",
            f"     rarity {hatched.pet_id.rarity.value}  id {hatched.pet_id.id}  {detail}",
        ]
        if source_egg.timer is not None and not source_egg.timer.has_ended(self._logic.player):
            remaining = source_egg.timer.calculate_remaining_seconds(self._logic.player)
            lines.extend(["", f"hatching… {remaining}s remaining"])
        elif self.canCompleteHatch and source_egg.is_equipped:
            lines.extend(["", "ready to hatch"])
        elif self.canStartHatch:
            lines.extend(["", "place in hatch slot to begin"])
        return lines
