from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, Signal, Slot

from config import PETS_MAPPING
from core.game_logic.actions import ActionResult
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_pet_collection_model import PlayerEggModel
from pet_collection_bridge import PetCollectionBridge


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
        self._prediction_text = "Click an egg in the collection or hatch slot to preview its hatch."
        self._status_text = self._build_status_text()
        self._last_action_text = ""

    def _build_status_text(self) -> str:
        collection = self._logic.player.player_pet_collection_model
        inventory_eggs = sum(1 for egg in collection.eggs if not egg.is_equipped)
        hatching_eggs = sum(1 for egg in collection.eggs if egg.is_equipped)
        return (
            f"eggs {len(collection.eggs)}  inventory {inventory_eggs}  "
            f"hatching {hatching_eggs}  hatch slots {collection.unlocked_hatch_slots_count}"
        )

    def _selected_egg(self) -> PlayerEggModel | None:
        if not self._selected_egg_guid:
            return None
        return _find_egg_by_guid(
            self._logic.player.player_pet_collection_model.eggs,
            self._selected_egg_guid,
        )

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

    @Property(bool, notify=stateChanged)
    def canHatchSelected(self) -> bool:
        egg = self._selected_egg()
        return egg is not None and egg.is_equipped

    @Slot(str)
    def predictHatch(self, egg_guid: str) -> None:
        self._selected_egg_guid = egg_guid
        self._prediction_text = "\n".join(self._build_hatch_prediction_lines(egg_guid))
        self._status_text = self._build_status_text()
        self.stateChanged.emit()

    @Slot()
    def performSelectedHatch(self) -> None:
        egg_guid = self._selected_egg_guid
        egg = self._selected_egg()
        if egg is None:
            self._last_action_text = "no egg selected"
            self.stateChanged.emit()
            return
        if not egg.is_equipped:
            self._last_action_text = "only eggs in hatch slots can be hatched here"
            self.stateChanged.emit()
            return

        result, hatched = self._logic.pet_egg_hatch_finalize(egg_guid, commit=True)
        if result != ActionResult.Success or hatched is None:
            self._last_action_text = f"hatch failed: {result.name}"
        else:
            detail = "NEW" if hatched.is_new else "duplicate"
            self._last_action_text = (
                f"hatched {_pet_key(hatched.pet_id)} "
                f"(rarity {hatched.pet_id.rarity.value}, id {hatched.pet_id.id}, {detail})"
            )
            self._prediction_text = self._last_action_text

        self._selected_egg_guid = ""
        if self._pet_collection is not None:
            self._pet_collection.refresh()
        self._status_text = self._build_status_text()
        self.stateChanged.emit()

    def _build_hatch_prediction_lines(self, egg_guid: str) -> list[str]:
        source_egg = _find_egg_by_guid(
            self._logic.player.player_pet_collection_model.eggs,
            egg_guid,
        )
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
            f"     guid {source_egg.guid[:24]}",
            "",
            f"pet  {_pet_key(hatched.pet_id)}",
            f"     rarity {hatched.pet_id.rarity.value}  id {hatched.pet_id.id}  {detail}",
        ]
        if source_egg.is_equipped:
            lines.extend(["", "ready to hatch — use Hatch button on the right"])
        return lines
