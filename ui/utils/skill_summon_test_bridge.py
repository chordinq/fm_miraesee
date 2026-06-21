from __future__ import annotations

import copy

from PySide6.QtCore import Property, QObject, QUrl, Signal, Slot

from config import SKILLS_MAPPING, SPRITES_DIR
from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id
from skill_collection_bridge import SkillCollectionBridge


def _skill_key(combat_skill) -> str:
    skill_id = combat_skill_to_skill_id(combat_skill)
    return SKILLS_MAPPING[f"{skill_id.rarity.value}_{skill_id.idx}"]["Key"]


class SkillSummonTestBridge(QObject):
    stateChanged = Signal()

    def __init__(self, logic: GameLogic, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._logic = logic
        player = logic.player
        summon_config = player.game_config.skill_summon_config
        self._summon_count = summon_config.get_base_summon_count()
        self._skill_collection = SkillCollectionBridge(
            player.player_skill_collection_model,
            parent=self,
        )
        self._prediction_text = ""
        self._status_text = ""
        self._last_action_text = ""
        self._summon_sprite_image = QUrl.fromLocalFile(
            str(SPRITES_DIR / "Currency" / "skillTicket.png")
        ).toString()
        self._sync_status()
        self._prediction_text = "\n".join(self._build_prediction_lines())

    def _sync_status(self) -> None:
        player = self._logic.player
        collection = player.player_skill_collection_model
        summon = collection.summon_model
        tickets = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
        cost = player.game_config.skill_summon_config.single_summon_cost
        total_cost = cost.amount * self._summon_count
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
        cost = self._logic.player.game_config.skill_summon_config.single_summon_cost
        return cost.amount * self._summon_count

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

    @Slot()
    def predictSummon(self) -> None:
        self._prediction_text = "\n".join(self._build_prediction_lines())
        self.stateChanged.emit()

    @Slot()
    def performSummon(self) -> None:
        count = self._summon_count
        result, summoned = self._logic.skill_summon(count, commit=True)
        if result != ActionResult.Success:
            self._last_action_text = f"summon failed: {result.name}"
        else:
            parts = [f"summon x{count} ok"]
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
        self._skill_collection.refresh()
        self._sync_status()
        self.predictSummon()
        self.stateChanged.emit()

    def _build_prediction_lines(self) -> list[str]:
        player = copy.deepcopy(self._logic.player)
        logic = GameLogic(player)
        collection = player.player_skill_collection_model
        summon = collection.summon_model
        tickets_before = player.player_currency_model.get(CurrencyType.SkillSummonTickets)
        seed_before = summon.seed
        level_before = summon.level
        count_before = summon.count

        result, summoned = logic.skill_summon(self._summon_count, commit=True)
        if result != ActionResult.Success:
            return [f"predict unavailable: {result.name}"]

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
                f"seed  {seed_before:#018x} -> {summon.seed:#018x}",
                f"meta  lv {level_before} -> {summon.level}  count {count_before} -> {summon.count}",
                f"tickets {tickets_before} -> {tickets_after}",
            ]
        )
        return lines
