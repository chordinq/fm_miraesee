from __future__ import annotations

from collections import defaultdict

from PySide6.QtCore import QObject, Property, QTimer, Signal, Slot

from config import TECHTREE_MAPPING, TECH_TREE_LIBRARY
from core.format.format_techtree import (
	build_tech_tree_node_description,
	build_tech_tree_node_description_lines,
	build_tech_tree_node_title,
	tier_roman_numeral,
)
from core.format.format_time import format_timer_duration
from core.game_logic.actions import ActionResult
from core.game_logic.enums import CurrencyType, GemSkipTarget, TechTreeNodeType, TechTreeType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_techtree_model import (
	TechTreeNodeModel,
	resolve_upgrade_level_info,
	upgrade_level_index,
)
from core.game_logic.player.timer_model import TimerModel
from controllers.support.currency_overdraft import can_afford_currency_for_ui
from controllers.common.ui_format import format_ui_integer
from ui.utils.ui_settings import game_number_formatting_enabled
from controllers.common.timer_bar_bridge import TimerBarBridge


_ACTION_PATCH_KEYS = (
    "upgrade_cost",
    "upgrade_cost_text",
    "upgrade_duration_text",
    "is_upgrading",
    "is_upgrade_complete",
    "other_research_in_progress",
    "can_start_upgrade",
    "skip_gem_cost",
    "skip_gem_cost_text",
    "can_afford_skip",
)


class TechTreeNodeBridge(QObject):
    changed = Signal()

    def __init__(
        self,
        player: PlayerModel,
        node_type: int,
        tree_type: int,
        node_id: int,
        layer: int,
        tier: int,
        x_ratio: float,
        level: int,
        icon_level: int,
        level_max: int,
        max_level: bool,
        requirements_met: bool,
        node_key: str,
        sprite_index: int,
        name_loc_id: str,
        name_loc_table: str,
        desc_loc_id: str,
        desc_loc_table: str,
        desc_format_args: list[str],
        name_text: str,
        desc_text: str,
        desc_lines: list[dict[str, str]],
        tier_roman: str,
        per_level_increase_text: str,
        upgrade_cost: int,
        upgrade_cost_text: str,
        upgrade_duration_text: str,
        is_upgrading: bool,
        is_upgrade_complete: bool,
        other_research_in_progress: bool,
        can_start_upgrade: bool,
        skip_gem_cost: int,
        skip_gem_cost_text: str,
        can_afford_skip: bool,
        ui_language: str = "en",
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._node_type = node_type
        self._tree_type = tree_type
        self._node_id = node_id
        self._layer = layer
        self._tier = tier
        self._x_ratio = x_ratio
        self._level = level
        self._icon_level = icon_level
        self._level_max = level_max
        self._max_level = max_level
        self._requirements_met = requirements_met
        self._node_key = node_key
        self._sprite_index = sprite_index
        self._name_loc_id = name_loc_id
        self._name_loc_table = name_loc_table
        self._desc_loc_id = desc_loc_id
        self._desc_loc_table = desc_loc_table
        self._desc_format_args = desc_format_args
        self._name_text = name_text
        self._desc_text = desc_text
        self._desc_lines = desc_lines
        self._tier_roman = tier_roman
        self._per_level_increase_text = per_level_increase_text
        self._upgrade_cost = upgrade_cost
        self._upgrade_cost_text = upgrade_cost_text
        self._upgrade_duration_text = upgrade_duration_text
        self._is_upgrading = is_upgrading
        self._is_upgrade_complete = is_upgrade_complete
        self._other_research_in_progress = other_research_in_progress
        self._can_start_upgrade = can_start_upgrade
        self._skip_gem_cost = skip_gem_cost
        self._skip_gem_cost_text = skip_gem_cost_text
        self._can_afford_skip = can_afford_skip
        self._ui_language = ui_language
        self._timer_bar = TimerBarBridge(parent=self)
        self._bind_timer()

    def update_from(
        self,
        player: PlayerModel,
        node_type: int,
        tree_type: int,
        node_id: int,
        layer: int,
        tier: int,
        x_ratio: float,
        level: int,
        icon_level: int,
        level_max: int,
        max_level: bool,
        requirements_met: bool,
        node_key: str,
        sprite_index: int,
        name_loc_id: str,
        name_loc_table: str,
        desc_loc_id: str,
        desc_loc_table: str,
        desc_format_args: list[str],
        name_text: str,
        desc_text: str,
        desc_lines: list[dict[str, str]],
        tier_roman: str,
        per_level_increase_text: str,
        upgrade_cost: int,
        upgrade_cost_text: str,
        upgrade_duration_text: str,
        is_upgrading: bool,
        is_upgrade_complete: bool,
        other_research_in_progress: bool,
        can_start_upgrade: bool,
        skip_gem_cost: int,
        skip_gem_cost_text: str,
        can_afford_skip: bool,
        ui_language: str = "en",
    ) -> None:
        self._player = player
        self._node_type = node_type
        self._tree_type = tree_type
        self._node_id = node_id
        self._layer = layer
        self._tier = tier
        self._x_ratio = x_ratio
        self._level = level
        self._icon_level = icon_level
        self._level_max = level_max
        self._max_level = max_level
        self._requirements_met = requirements_met
        self._node_key = node_key
        self._sprite_index = sprite_index
        self._name_loc_id = name_loc_id
        self._name_loc_table = name_loc_table
        self._desc_loc_id = desc_loc_id
        self._desc_loc_table = desc_loc_table
        self._desc_format_args = desc_format_args
        self._name_text = name_text
        self._desc_text = desc_text
        self._desc_lines = desc_lines
        self._tier_roman = tier_roman
        self._per_level_increase_text = per_level_increase_text
        self._upgrade_cost = upgrade_cost
        self._upgrade_cost_text = upgrade_cost_text
        self._upgrade_duration_text = upgrade_duration_text
        self._is_upgrading = is_upgrading
        self._is_upgrade_complete = is_upgrade_complete
        self._other_research_in_progress = other_research_in_progress
        self._can_start_upgrade = can_start_upgrade
        self._skip_gem_cost = skip_gem_cost
        self._skip_gem_cost_text = skip_gem_cost_text
        self._can_afford_skip = can_afford_skip
        self._ui_language = ui_language
        self._bind_timer()
        self.changed.emit()

    def patch_action_state(
        self,
        player: PlayerModel,
        *,
        level: int | None = None,
        icon_level: int | None = None,
        max_level: bool | None = None,
        requirements_met: bool | None = None,
        desc_text: str | None = None,
        desc_lines: list[dict[str, str]] | None = None,
        upgrade_cost: int | None = None,
        upgrade_cost_text: str | None = None,
        upgrade_duration_text: str | None = None,
        is_upgrading: bool | None = None,
        is_upgrade_complete: bool | None = None,
        other_research_in_progress: bool | None = None,
        can_start_upgrade: bool | None = None,
        skip_gem_cost: int | None = None,
        skip_gem_cost_text: str | None = None,
        can_afford_skip: bool | None = None,
    ) -> None:
        self._player = player
        changed = False
        rebind_timer = False

        def _set(name: str, value: object) -> None:
            nonlocal changed, rebind_timer
            if value is None:
                return
            if getattr(self, name) != value:
                setattr(self, name, value)
                changed = True
                if name in (
                    "_is_upgrading",
                    "_is_upgrade_complete",
                    "_skip_gem_cost",
                    "_skip_gem_cost_text",
                    "_can_afford_skip",
                ):
                    rebind_timer = True

        _set("_level", level)
        _set("_icon_level", icon_level)
        _set("_max_level", max_level)
        _set("_requirements_met", requirements_met)
        _set("_desc_text", desc_text)
        _set("_desc_lines", desc_lines)
        _set("_upgrade_cost", upgrade_cost)
        _set("_upgrade_cost_text", upgrade_cost_text)
        _set("_upgrade_duration_text", upgrade_duration_text)
        _set("_is_upgrading", is_upgrading)
        _set("_is_upgrade_complete", is_upgrade_complete)
        _set("_other_research_in_progress", other_research_in_progress)
        _set("_can_start_upgrade", can_start_upgrade)
        _set("_skip_gem_cost", skip_gem_cost)
        _set("_skip_gem_cost_text", skip_gem_cost_text)
        _set("_can_afford_skip", can_afford_skip)

        if not changed:
            return
        if rebind_timer:
            self._bind_timer()
        self.changed.emit()

    def update_localized_texts(
        self,
        *,
        name_text: str,
        desc_text: str,
        desc_lines: list[dict[str, str]],
        upgrade_duration_text: str,
        ui_language: str,
    ) -> None:
        self._name_text = name_text
        self._desc_text = desc_text
        self._desc_lines = desc_lines
        self._upgrade_duration_text = upgrade_duration_text
        self._ui_language = ui_language
        self._timer_bar.set_ui_language(ui_language)
        self.changed.emit()

    def _bind_timer(self) -> None:
        techtree = self._player.player_techtree_model
        node_model = techtree.get_node(TechTreeType(self._tree_type), self._node_id)
        if node_model is None or not (self._is_upgrading or self._is_upgrade_complete):
            self._timer_bar.clear()
            return
        timer = node_model.node_upgrade_timer_model
        if timer.start_time <= 0:
            self._timer_bar.clear()
            return
        self._timer_bar.bind(timer, self._player, language=self._ui_language)

    @Property(int, notify=changed)
    def nodeType(self) -> int:
        return self._node_type

    @Property(int, notify=changed)
    def treeType(self) -> int:
        return self._tree_type

    @Property(int, notify=changed)
    def nodeId(self) -> int:
        return self._node_id

    @Property(int, notify=changed)
    def layer(self) -> int:
        return self._layer

    @Property(int, notify=changed)
    def tier(self) -> int:
        return self._tier

    @Property(float, notify=changed)
    def xRatio(self) -> float:
        return self._x_ratio

    @Property(int, notify=changed)
    def level(self) -> int:
        return self._level

    @Property(int, notify=changed)
    def iconLevel(self) -> int:
        return self._icon_level

    @Property(int, notify=changed)
    def levelMax(self) -> int:
        return self._level_max

    @Property(bool, notify=changed)
    def maxLevel(self) -> bool:
        return self._max_level

    @Property(bool, notify=changed)
    def requirementsMet(self) -> bool:
        return self._requirements_met

    @Property(str, notify=changed)
    def nodeKey(self) -> str:
        return self._node_key

    @Property(int, notify=changed)
    def spriteIndex(self) -> int:
        return self._sprite_index

    @Property(str, notify=changed)
    def nameText(self) -> str:
        return self._name_text

    @Property(str, notify=changed)
    def descText(self) -> str:
        return self._desc_text

    @Property("QVariantList", notify=changed)
    def descLines(self) -> list[dict[str, str]]:
        return self._desc_lines

    @Property(str, notify=changed)
    def nameLocId(self) -> str:
        return self._name_loc_id

    @Property(str, notify=changed)
    def nameLocTable(self) -> str:
        return self._name_loc_table

    @Property(str, notify=changed)
    def descLocId(self) -> str:
        return self._desc_loc_id

    @Property(str, notify=changed)
    def descLocTable(self) -> str:
        return self._desc_loc_table

    @Property("QVariantList", notify=changed)
    def descFormatArgs(self) -> list[str]:
        return self._desc_format_args

    @Property(str, notify=changed)
    def tierRoman(self) -> str:
        return self._tier_roman

    @Property(str, notify=changed)
    def perLevelIncreaseText(self) -> str:
        return self._per_level_increase_text

    @Property(int, notify=changed)
    def upgradeCost(self) -> int:
        return self._upgrade_cost

    @Property(str, notify=changed)
    def upgradeCostText(self) -> str:
        return self._upgrade_cost_text

    @Property(str, notify=changed)
    def upgradeDurationText(self) -> str:
        return self._upgrade_duration_text

    @Property(bool, notify=changed)
    def isUpgrading(self) -> bool:
        return self._is_upgrading

    @Property(bool, notify=changed)
    def isUpgradeComplete(self) -> bool:
        return self._is_upgrade_complete

    @Property(bool, notify=changed)
    def otherResearchInProgress(self) -> bool:
        return self._other_research_in_progress

    @Property(bool, notify=changed)
    def canStartUpgrade(self) -> bool:
        return self._can_start_upgrade

    @Property(int, notify=changed)
    def skipGemCost(self) -> int:
        return self._skip_gem_cost

    @Property(str, notify=changed)
    def skipGemCostText(self) -> str:
        return self._skip_gem_cost_text

    @Property(bool, notify=changed)
    def canAffordSkip(self) -> bool:
        return self._can_afford_skip

    @Property(QObject, constant=True)
    def timerBridge(self) -> TimerBarBridge:
        return self._timer_bar


class TechTreeCollectionBridge(QObject):
    changed = Signal()
    statsChanged = Signal()
    economyChanged = Signal()
    progressChanged = Signal()
    categoryResearchChanged = Signal()

    def __init__(
        self,
        logic: GameLogic,
        tree_type: TechTreeType = TechTreeType.SkillsPetTech,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._logic = logic
        self._player = logic.player
        self._tree_type = tree_type
        self._ui_language = "en"
        self._category_timer_bar = TimerBarBridge(parent=self)
        self._category_timer_bar.displayChanged.connect(self.categoryResearchChanged.emit)
        self._rebuild()

    def reload(self, logic: GameLogic) -> None:
        self._logic = logic
        self._player = logic.player
        self._rebuild()
        self.changed.emit()
        self.progressChanged.emit()
        self.categoryResearchChanged.emit()

    @Slot()
    def refresh(self) -> None:
        self._rebuild()
        self.changed.emit()
        self.progressChanged.emit()
        self.categoryResearchChanged.emit()

    def sync_nodes(self) -> None:
        if not getattr(self, "_nodes", None):
            self.refresh()
            return
        for bridge in self._nodes:
            self._sync_bridge(bridge)
        self._emit_tree_progress()

    def _emit_tree_progress(self) -> None:
        techtree = self._player.player_techtree_model
        self._progress_level_sum, self._progress_max_sum = (
            techtree.get_tech_tree_progress_parts(self._player, self._tree_type)
        )
        self._progress = (
            float(self._progress_level_sum) / float(self._progress_max_sum)
            if self._progress_max_sum > 0
            else 0.0
        )
        self._sync_category_timer()
        self.progressChanged.emit()
        self.categoryResearchChanged.emit()

    def _patch_research_gates(self, bridge: TechTreeNodeBridge) -> None:
        node_model = self._player.player_techtree_model.get_node(
            self._tree_type,
            bridge._node_id,
        )
        fields = self._build_node_fields(
            bridge._node_id,
            bridge._node_type,
            bridge._tier,
            node_model,
            bridge._level,
            bridge._level_max,
            bridge._max_level,
            bridge._requirements_met,
        )
        bridge.patch_action_state(
            self._player,
            **{key: fields[key] for key in _ACTION_PATCH_KEYS},
        )

    def _patch_node_state(
        self,
        bridge: TechTreeNodeBridge,
        *,
        refresh_desc: bool,
        refresh_requirements: bool,
    ) -> None:
        try:
            node_type = TechTreeNodeType(bridge._node_type)
        except ValueError:
            return

        techtree = self._player.player_techtree_model
        if refresh_requirements:
            try:
                requirements_met = techtree.node_requirements_met(
                    self._player,
                    self._tree_type,
                    bridge._node_id,
                )
            except ValueError:
                requirements_met = False
        else:
            requirements_met = bridge._requirements_met

        node_model = techtree.get_node(self._tree_type, bridge._node_id)
        icon_level = self._icon_level(node_model, requirements_met)
        ui_level = self._display_ui_level(node_model)
        is_max = self._is_max_display(node_model, bridge._level_max)
        fields = self._build_node_fields(
            bridge._node_id,
            bridge._node_type,
            bridge._tier,
            node_model,
            ui_level,
            bridge._level_max,
            is_max,
            requirements_met,
        )
        patch_kwargs: dict[str, object] = {
            "level": ui_level,
            "icon_level": icon_level,
            "max_level": is_max,
            "requirements_met": requirements_met,
            **{key: fields[key] for key in _ACTION_PATCH_KEYS},
        }
        if refresh_desc:
            _, desc_text, desc_lines = self._node_display_texts(
                node_type,
                bridge._tier,
                node_model,
                bridge._level_max,
                self._ui_language,
            )
            patch_kwargs["desc_text"] = desc_text
            patch_kwargs["desc_lines"] = desc_lines
        bridge.patch_action_state(self._player, **patch_kwargs)

    def _patch_requirements_only(self, bridge: TechTreeNodeBridge) -> None:
        techtree = self._player.player_techtree_model
        try:
            requirements_met = techtree.node_requirements_met(
                self._player,
                self._tree_type,
                bridge._node_id,
            )
        except ValueError:
            requirements_met = False

        node_model = techtree.get_node(self._tree_type, bridge._node_id)
        icon_level = self._icon_level(node_model, requirements_met)
        fields = self._build_node_fields(
            bridge._node_id,
            bridge._node_type,
            bridge._tier,
            node_model,
            bridge._level,
            bridge._level_max,
            bridge._max_level,
            requirements_met,
        )
        if (
            requirements_met == bridge._requirements_met
            and icon_level == bridge._icon_level
            and fields["can_start_upgrade"] == bridge._can_start_upgrade
            and fields["other_research_in_progress"] == bridge._other_research_in_progress
        ):
            return
        bridge.patch_action_state(
            self._player,
            icon_level=icon_level,
            requirements_met=requirements_met,
            **{key: fields[key] for key in _ACTION_PATCH_KEYS},
        )

    def _dependent_node_ids(self, node_id: int) -> list[int]:
        dependents = getattr(self, "_dependents_by_node", {})
        queue = list(dependents.get(node_id, []))
        ordered: list[int] = []
        seen: set[int] = set()
        while queue:
            current = queue.pop(0)
            if current in seen:
                continue
            seen.add(current)
            ordered.append(current)
            queue.extend(dependents.get(current, []))
        return ordered

    def patch_after_research_start(self, node_id: int) -> None:
        bridge = self.nodeById(node_id)
        if bridge is not None:
            self._patch_node_state(
                bridge,
                refresh_desc=False,
                refresh_requirements=False,
            )
        for other in self._nodes:
            if other._node_id != node_id:
                self._patch_research_gates(other)
        self._emit_tree_progress()

    def patch_after_gem_skip(self, node_id: int) -> None:
        bridge = self.nodeById(node_id)
        if bridge is not None:
            self._patch_node_state(
                bridge,
                refresh_desc=False,
                refresh_requirements=False,
            )
        self._emit_tree_progress()

    def patch_after_claim(self, node_id: int) -> None:
        bridge = self.nodeById(node_id)
        if bridge is not None:
            self._patch_node_state(
                bridge,
                refresh_desc=True,
                refresh_requirements=False,
            )
        for dependent_id in self._dependent_node_ids(node_id):
            dependent = self.nodeById(dependent_id)
            if dependent is not None:
                self._patch_requirements_only(dependent)
        self._emit_tree_progress()

    def patch_when_research_settles(self) -> None:
        techtree = self._player.player_techtree_model
        for bridge in self._nodes:
            node_model = techtree.get_node(self._tree_type, bridge._node_id)
            timer = node_model.node_upgrade_timer_model if node_model is not None else None
            if (
                bridge._is_upgrading
                or bridge._is_upgrade_complete
                or (timer is not None and timer.start_time > 0)
            ):
                self._patch_node_state(
                    bridge,
                    refresh_desc=False,
                    refresh_requirements=False,
                )
            elif bridge._other_research_in_progress:
                self._patch_research_gates(bridge)
        self._emit_tree_progress()

    def patch_upgrade_affordability(self) -> None:
        for bridge in self._nodes:
            self._patch_research_gates(bridge)
        self.progressChanged.emit()

    def _node_key(self, node_type: int) -> str:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        return str(entry.get("Key", ""))

    def _sprite_index(self, node_type: int) -> int:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        sprite = entry.get("Sprite")
        if sprite is None:
            return -1
        return int(sprite["Idx"])

    @staticmethod
    def _node_display_texts(
        node_type: TechTreeNodeType,
        tier: int,
        node_model: TechTreeNodeModel | None,
        level_max: int,
        language: str,
    ) -> tuple[str, str, list[dict[str, str]]]:
        lib_entry = TECH_TREE_LIBRARY.get(node_type.name)
        internal_level = node_model.level if node_model is not None else -1
        name_text = build_tech_tree_node_title(node_type, tier, language=language)
        if lib_entry is None:
            return name_text, "", []
        desc_lines = build_tech_tree_node_description_lines(
            lib_entry,
            node_type=node_type,
            internal_level=internal_level,
            level_max=level_max,
            tier=tier,
            language=language,
        )
        desc_text = build_tech_tree_node_description(
            lib_entry,
            node_type=node_type,
            internal_level=internal_level,
            level_max=level_max,
            tier=tier,
            language=language,
        )
        line_models = [
            {"text": line.text, "deltaText": line.delta_text}
            for line in desc_lines
        ]
        return name_text, desc_text, line_models

    def _level_max(self, node_type: TechTreeNodeType) -> int:
        lib_entry = TECH_TREE_LIBRARY.get(node_type.name)
        if lib_entry is None:
            return 0
        return int(lib_entry.get("MaxLevel", 0))

    @staticmethod
    def _layer_x_ratio(index: int, count: int) -> float:
        if count <= 1:
            return 0.5
        return (index + 0.5) / count

    @staticmethod
    def _timer_is_running(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        if node_model is None:
            return False
        timer = node_model.node_upgrade_timer_model
        return timer.start_time > 0 and not timer.has_ended(player)

    @staticmethod
    def _timer_is_claimable(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        if node_model is None:
            return False
        timer = node_model.node_upgrade_timer_model
        return timer.start_time > 0 and timer.has_ended(player)

    @staticmethod
    def _timer_active(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        return TechTreeCollectionBridge._timer_is_running(player, node_model)

    @staticmethod
    def _timer_complete(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        return TechTreeCollectionBridge._timer_is_claimable(player, node_model)

    def _other_research_in_progress(
        self,
        tree_type: TechTreeType,
        node_id: int,
    ) -> bool:
        techtree = self._player.player_techtree_model
        for active_tree_type, nodes in techtree.tech_trees.items():
            for active_node_id, node_model in nodes.items():
                if active_tree_type == tree_type and active_node_id == node_id:
                    continue
                timer = node_model.node_upgrade_timer_model
                if timer.start_time > 0 and not timer.has_ended(self._player):
                    return True
        return False

    def _display_ui_level(self, node_model) -> int:
        if node_model is None:
            return 0
        return max(0, int(node_model.level) + 1)

    def _is_max_display(self, node_model, level_max: int) -> bool:
        if level_max <= 0 or node_model is None:
            return False
        if self._timer_active(self._player, node_model):
            return False
        return self._display_ui_level(node_model) == level_max

    def _icon_level(
        self,
        node_model,
        requirements_met: bool,
    ) -> int:
        if not requirements_met:
            return -2
        if node_model is None:
            return -2
        if self._timer_active(self._player, node_model):
            return -1
        if node_model.level < 0:
            return -2
        return int(node_model.level)

    def _build_node_fields(
        self,
        node_id: int,
        node_type_value: int,
        tier: int,
        node_model: TechTreeNodeModel | None,
        ui_level: int,
        level_max: int,
        is_max: bool,
        requirements_met: bool,
    ) -> dict:
        is_upgrading = self._timer_active(self._player, node_model)
        is_upgrade_complete = self._timer_complete(self._player, node_model)
        other_research = self._other_research_in_progress(
            self._tree_type,
            node_id,
        )

        upgrade_cost = 0
        upgrade_cost_text = ""
        upgrade_duration_text = ""
        skip_gem_cost = 0
        skip_gem_cost_text = ""
        can_afford_skip = False

        if not is_max:
            upgrade_info = resolve_upgrade_level_info(
                self._player,
                tier,
                upgrade_level_index(node_model),
            )
            if upgrade_info is not None:
                upgrade_cost, duration_seconds = upgrade_info
                upgrade_cost_text = format_ui_integer(upgrade_cost)
                upgrade_duration_text = format_timer_duration(
                    duration_seconds,
                    self._ui_language,
                    game_number_formatting_enabled=game_number_formatting_enabled(),
                )

        if node_model is not None and (is_upgrading or is_upgrade_complete):
            skip_gem_cost = node_model.node_upgrade_timer_model.calculate_gem_skip_cost(
                self._player,
                GemSkipTarget.TechTree,
            )
            skip_gem_cost_text = format_ui_integer(skip_gem_cost)
            can_afford_skip = can_afford_currency_for_ui(
                self._player,
                CurrencyType.Gems,
                skip_gem_cost,
            )

        can_afford_upgrade = can_afford_currency_for_ui(
            self._player,
            CurrencyType.TechPotions,
            upgrade_cost,
        )
        can_start_upgrade = (
            requirements_met
            and not is_max
            and not is_upgrading
            and not is_upgrade_complete
            and not other_research
            and upgrade_cost > 0
            and can_afford_upgrade
        )

        return {
            "tier_roman": tier_roman_numeral(tier),
            "per_level_increase_text": "",
            "upgrade_cost": upgrade_cost,
            "upgrade_cost_text": upgrade_cost_text,
            "upgrade_duration_text": upgrade_duration_text,
            "is_upgrading": is_upgrading,
            "is_upgrade_complete": is_upgrade_complete,
            "other_research_in_progress": other_research and not is_upgrading,
            "can_start_upgrade": can_start_upgrade,
            "skip_gem_cost": skip_gem_cost,
            "skip_gem_cost_text": skip_gem_cost_text,
            "can_afford_skip": can_afford_skip and is_upgrading,
        }

    def _collect_node_bridge_payload(
        self,
        *,
        node_id: int,
        node_type: TechTreeNodeType,
        layer: int,
        tier: int,
        x_ratio: float,
    ) -> dict:
        techtree = self._player.player_techtree_model
        level_max = self._level_max(node_type)

        try:
            requirements_met = techtree.node_requirements_met(
                self._player,
                self._tree_type,
                node_id,
            )
        except ValueError:
            requirements_met = False

        node_model = techtree.get_node(self._tree_type, node_id)
        icon_level = self._icon_level(node_model, requirements_met)
        ui_level = self._display_ui_level(node_model)
        is_max = self._is_max_display(node_model, level_max)
        node_type_value = int(node_type.value)
        name_text, desc_text, desc_lines = self._node_display_texts(
            node_type,
            tier,
            node_model,
            level_max,
            self._ui_language,
        )
        detail_fields = self._build_node_fields(
            node_id,
            node_type_value,
            tier,
            node_model,
            ui_level,
            level_max,
            is_max,
            requirements_met,
        )
        return {
            "node_type": node_type_value,
            "tree_type": int(self._tree_type.value),
            "node_id": node_id,
            "layer": layer,
            "tier": tier,
            "x_ratio": x_ratio,
            "level": ui_level,
            "icon_level": icon_level,
            "level_max": level_max,
            "max_level": is_max,
            "requirements_met": requirements_met,
            "node_key": self._node_key(node_type_value),
            "sprite_index": self._sprite_index(node_type_value),
            "name_loc_id": "",
            "name_loc_table": "TechTree",
            "desc_loc_id": "",
            "desc_loc_table": "TechTree",
            "desc_format_args": [],
            "name_text": name_text,
            "desc_text": desc_text,
            "desc_lines": desc_lines,
            "ui_language": self._ui_language,
            **detail_fields,
        }

    def _sync_bridge(self, bridge: TechTreeNodeBridge) -> None:
        try:
            node_type = TechTreeNodeType(bridge._node_type)
        except ValueError:
            return
        payload = self._collect_node_bridge_payload(
            node_id=bridge._node_id,
            node_type=node_type,
            layer=bridge._layer,
            tier=bridge._tier,
            x_ratio=bridge._x_ratio,
        )
        bridge.update_from(self._player, **payload)

    def _apply_node_upgrade_claim(self, node_id: int) -> bool:
        result = self._logic.tech_tree_node_upgrade_claim(
            self._tree_type,
            node_id,
            commit=True,
        )
        return result == ActionResult.Success

    def _claim_all_finished_nodes(self) -> bool:
        techtree = self._player.player_techtree_model
        node_ids = list(techtree.tech_trees.get(self._tree_type, {}).keys())
        claimed_any = False
        for node_id in node_ids:
            if self._apply_node_upgrade_claim(node_id):
                claimed_any = True
        if claimed_any:
            self._schedule_stats_changed()
        return claimed_any

    def _find_category_research_node(self) -> TechTreeNodeModel | None:
        techtree = self._player.player_techtree_model
        for node_model in techtree.tech_trees.get(self._tree_type, {}).values():
            timer = node_model.node_upgrade_timer_model
            if timer.start_time > 0:
                return node_model
        return None

    def _sync_category_timer(self) -> None:
        node_model = self._find_category_research_node()
        if node_model is None:
            self._category_timer_bar.clear()
            return
        self._category_timer_bar.bind(
            node_model.node_upgrade_timer_model,
            self._player,
            language=self._ui_language,
        )

    def _rebuild(self) -> None:
        position_library = self._player.game_config.tech_tree_position_library
        tree_data = position_library.get(self._tree_type)
        techtree = self._player.player_techtree_model

        existing_by_id = {bridge._node_id: bridge for bridge in getattr(self, "_nodes", [])}
        nodes: list[TechTreeNodeBridge] = []
        connections: list[dict[str, int]] = []
        max_layer = 0
        layer_rows: list[dict] = []

        if tree_data is not None:
            layer_groups: dict[int, list[dict]] = defaultdict(list)
            for node_info in tree_data.get("Nodes", []):
                layer_groups[int(node_info["Layer"])].append(node_info)

            if layer_groups:
                max_layer = max(layer_groups)

            for layer in sorted(layer_groups):
                layer_nodes = sorted(layer_groups[layer], key=lambda node: int(node["Id"]))
                count = len(layer_nodes)
                for index, node_info in enumerate(layer_nodes):
                    try:
                        node_type = TechTreeNodeType[node_info["Type"]]
                    except KeyError:
                        continue

                    node_id = int(node_info["Id"])
                    tier = int(node_info.get("Tier", 0))
                    x_ratio = self._layer_x_ratio(index, count)
                    payload = self._collect_node_bridge_payload(
                        node_id=node_id,
                        node_type=node_type,
                        layer=layer,
                        tier=tier,
                        x_ratio=x_ratio,
                    )
                    if node_id in existing_by_id:
                        bridge = existing_by_id[node_id]
                        bridge.update_from(self._player, **payload)
                    else:
                        bridge = TechTreeNodeBridge(
                            self._player,
                            parent=self,
                            **payload,
                        )

                    nodes.append(bridge)

                    for req_id in node_info.get("Requirements", []):
                        connections.append(
                            {
                                "fromId": int(req_id),
                                "toId": node_id,
                            }
                        )

            nodes_by_layer: dict[int, list[TechTreeNodeBridge]] = defaultdict(list)
            for bridge in nodes:
                nodes_by_layer[bridge._layer].append(bridge)
            layer_rows = [
                {"layer": layer, "nodes": nodes_by_layer[layer]}
                for layer in sorted(nodes_by_layer)
            ]

        self._nodes = nodes
        self._connections = connections
        self._max_layer = max_layer
        self._node_count = len(nodes)
        self._progress_level_sum, self._progress_max_sum = (
            techtree.get_tech_tree_progress_parts(self._player, self._tree_type)
        )
        self._progress = (
            float(self._progress_level_sum) / float(self._progress_max_sum)
            if self._progress_max_sum > 0
            else 0.0
        )
        self._layer_rows = layer_rows
        dependents: dict[int, list[int]] = defaultdict(list)
        for connection in connections:
            dependents[int(connection["fromId"])].append(int(connection["toId"]))
        self._dependents_by_node = dict(dependents)
        self._sync_category_timer()

    def _refresh_localized(self) -> None:
        techtree = self._player.player_techtree_model
        language = self._ui_language
        for bridge in self._nodes:
            try:
                node_type = TechTreeNodeType(bridge._node_type)
            except ValueError:
                continue
            node_model = techtree.get_node(self._tree_type, bridge._node_id)
            name_text, desc_text, desc_lines = self._node_display_texts(
                node_type,
                bridge._tier,
                node_model,
                bridge._level_max,
                language,
            )
            upgrade_duration_text = bridge._upgrade_duration_text
            if not bridge._max_level:
                upgrade_info = resolve_upgrade_level_info(
                    self._player,
                    bridge._tier,
                    upgrade_level_index(node_model),
                )
                if upgrade_info is not None:
                    _, duration_seconds = upgrade_info
                    upgrade_duration_text = format_timer_duration(
                        duration_seconds,
                        language,
                        game_number_formatting_enabled=game_number_formatting_enabled(),
                    )
            bridge.update_localized_texts(
                name_text=name_text,
                desc_text=desc_text,
                desc_lines=desc_lines,
                upgrade_duration_text=upgrade_duration_text,
                ui_language=language,
            )
        self._category_timer_bar.set_ui_language(language)

    @Slot(int)
    def performUpgradeStart(self, node_id: int) -> None:
        result = self._logic.tech_tree_node_upgrade_start(
            self._tree_type,
            node_id,
            commit=True,
        )
        if result != ActionResult.Success:
            return
        self.patch_after_research_start(node_id)
        self._notify_economy_changed()

    def _schedule_stats_changed(self) -> None:
        QTimer.singleShot(0, self.statsChanged.emit)

    def _notify_economy_changed(self) -> None:
        self.economyChanged.emit()

    @Slot(int)
    def performGemSkip(self, node_id: int) -> None:
        result = self._logic.tech_tree_node_upgrade_gem_skip(
            self._tree_type,
            node_id,
            commit=True,
        )
        if result != ActionResult.Success:
            return
        self.patch_after_gem_skip(node_id)
        self._notify_economy_changed()

    @Slot(int)
    def performUpgradeClaim(self, node_id: int) -> None:
        if not self._apply_node_upgrade_claim(node_id):
            return
        self.patch_after_claim(node_id)
        self._schedule_stats_changed()

    @Slot()
    def tick(self) -> None:
        self._category_timer_bar.refresh()

    @Slot(str)
    def setUiLanguage(self, language: str) -> None:
        if language == self._ui_language:
            return
        self._ui_language = language
        self._refresh_localized()

    @Property(int, notify=changed)
    def treeType(self) -> int:
        return int(self._tree_type.value)

    @Property(float, notify=progressChanged)
    def progress(self) -> float:
        return self._progress

    @Property(int, notify=progressChanged)
    def progressLevelSum(self) -> int:
        return self._progress_level_sum

    @Property(int, notify=progressChanged)
    def progressMaxSum(self) -> int:
        return self._progress_max_sum

    @Property(bool, notify=categoryResearchChanged)
    def categoryResearchActive(self) -> bool:
        return (
            self._category_timer_bar.isActive
            and not self._category_timer_bar.isComplete
        )

    @Property(bool, notify=categoryResearchChanged)
    def categoryResearchComplete(self) -> bool:
        return self._category_timer_bar.isComplete

    @Property(str, notify=categoryResearchChanged)
    def categoryResearchRemainingText(self) -> str:
        return self._category_timer_bar.remainingText

    @Property(int, notify=changed)
    def maxLayer(self) -> int:
        return self._max_layer

    @Property(int, notify=changed)
    def nodeCount(self) -> int:
        return self._node_count

    @Property("QVariantList", notify=changed)
    def nodes(self) -> list[TechTreeNodeBridge]:
        return self._nodes

    @Property("QVariantList", notify=changed)
    def connections(self) -> list[dict[str, int]]:
        return self._connections

    @Property("QVariantList", notify=changed)
    def layerRows(self) -> list[dict]:
        return self._layer_rows

    @Slot(int, result=QObject)
    def nodeById(self, node_id: int) -> TechTreeNodeBridge | None:
        for bridge in self._nodes:
            if bridge._node_id == node_id:
                return bridge
        return None
