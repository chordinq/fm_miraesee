from __future__ import annotations

from collections import defaultdict

from PySide6.QtCore import QObject, Property, Signal, Slot

from config import TECHTREE_MAPPING, TECH_TREE_LIBRARY
from core.game_logic.enums import CurrencyType, GemSkipTarget, TechTreeNodeType, TechTreeType
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_techtree_model import TechTreeNodeModel
from core.game_logic.player.timer_model import TimerModel
from core.game_logic.player.player_currency_model import can_afford
from number_display_format import format_ui_integer
from timer_bar_bridge import TimerBarBridge
from localizer import desc_loc_from_entry, name_loc_from_entry
from tech_tree_stat_display import (
    build_tech_tree_desc_format_args,
    build_tech_tree_per_level_increase,
    format_upgrade_duration,
    lookup_upgrade_level_info,
    tier_roman_numeral,
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
        self._bind_timer()
        self.changed.emit()

    def _bind_timer(self) -> None:
        techtree = self._player.player_techtree_model
        node_model = techtree.get_node(TechTreeType(self._tree_type), self._node_id)
        if node_model is None or not (self._is_upgrading or self._is_upgrade_complete):
            self._timer_bar.clear()
            return
        timer = node_model.node_upgrade_timer_model
        if timer.end_time <= timer.start_time:
            self._timer_bar.clear()
            return
        self._timer_bar.bind(timer, self._player)

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

    def __init__(
        self,
        player: PlayerModel,
        tree_type: TechTreeType = TechTreeType.SkillsPetTech,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._player = player
        self._tree_type = tree_type
        self._refresh()

    def reload(self, player: PlayerModel) -> None:
        self._player = player
        self._refresh()
        self.changed.emit()

    def refresh(self) -> None:
        self._refresh()
        self.changed.emit()

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
    def _name_loc(node_type: int) -> tuple[str, str]:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        if not entry.get("Localization"):
            return "", "TechTree"
        return name_loc_from_entry(entry)

    @staticmethod
    def _desc_loc(node_type: int) -> tuple[str, str]:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        if not entry.get("DescLocalization"):
            return "", "TechTree"
        return desc_loc_from_entry(entry)

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
    def _timer_active(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        if node_model is None:
            return False
        timer = node_model.node_upgrade_timer_model
        return timer.end_time > timer.start_time and not timer.has_ended(player)

    @staticmethod
    def _timer_complete(player: PlayerModel, node_model: TechTreeNodeModel | None) -> bool:
        if node_model is None:
            return False
        timer = node_model.node_upgrade_timer_model
        return timer.end_time > timer.start_time and timer.has_ended(player)

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
                if timer.end_time > timer.start_time and not timer.has_ended(self._player):
                    return True
        return False

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
        internal_level = max(0, ui_level - 1)
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
            upgrade_info = lookup_upgrade_level_info(
                self._player.game_config,
                tier,
                internal_level,
            )
            if upgrade_info is not None:
                upgrade_cost, duration_seconds = upgrade_info
                upgrade_cost_text = format_ui_integer(upgrade_cost)
                upgrade_duration_text = format_upgrade_duration(duration_seconds)

        if node_model is not None and (is_upgrading or is_upgrade_complete):
            skip_gem_cost = node_model.node_upgrade_timer_model.calculate_gem_skip_cost(
                self._player,
                GemSkipTarget.TechTree,
            )
            skip_gem_cost_text = format_ui_integer(skip_gem_cost)
            can_afford_skip = self._player.player_currency_model.can_afford(
                CurrencyType.Gems,
                skip_gem_cost,
            )

        can_afford_upgrade = self._player.player_currency_model.can_afford(
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
            "per_level_increase_text": build_tech_tree_per_level_increase(
                node_type_value,
                tier,
            ),
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

    def _refresh(self) -> None:
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
                    ui_level = node_model.level + 1 if node_model is not None else 0
                    is_max = ui_level >= level_max if level_max > 0 else False
                    node_type_value = int(node_type.value)
                    name_loc_id, name_loc_table = self._name_loc(node_type_value)
                    desc_loc_id, desc_loc_table = self._desc_loc(node_type_value)
                    desc_format_args = build_tech_tree_desc_format_args(
                        node_type_value,
                        tier,
                        ui_level,
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
                    if node_id in existing_by_id:
                        bridge = existing_by_id[node_id]
                        bridge.update_from(
                            self._player,
                            node_type=node_type_value,
                            tree_type=int(self._tree_type.value),
                            node_id=node_id,
                            layer=layer,
                            tier=tier,
                            x_ratio=x_ratio,
                            level=ui_level,
                            icon_level=icon_level,
                            level_max=level_max,
                            max_level=is_max,
                            requirements_met=requirements_met,
                            node_key=self._node_key(node_type_value),
                            sprite_index=self._sprite_index(node_type_value),
                            name_loc_id=name_loc_id,
                            name_loc_table=name_loc_table,
                            desc_loc_id=desc_loc_id,
                            desc_loc_table=desc_loc_table,
                            desc_format_args=desc_format_args,
                            **detail_fields,
                        )
                    else:
                        bridge = TechTreeNodeBridge(
                            self._player,
                            node_type=node_type_value,
                            tree_type=int(self._tree_type.value),
                            node_id=node_id,
                            layer=layer,
                            tier=tier,
                            x_ratio=x_ratio,
                            level=ui_level,
                            icon_level=icon_level,
                            level_max=level_max,
                            max_level=is_max,
                            requirements_met=requirements_met,
                            node_key=self._node_key(node_type_value),
                            sprite_index=self._sprite_index(node_type_value),
                            name_loc_id=name_loc_id,
                            name_loc_table=name_loc_table,
                            desc_loc_id=desc_loc_id,
                            desc_loc_table=desc_loc_table,
                            desc_format_args=desc_format_args,
                            **detail_fields,
                            parent=self,
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
        self._progress = techtree.get_tech_tree_progress(self._player, self._tree_type)
        self._layer_rows = layer_rows

    def _ensure_node(self, node_id: int) -> TechTreeNodeModel:
        techtree = self._player.player_techtree_model
        node_model = techtree.get_node(self._tree_type, node_id)
        if node_model is not None:
            return node_model
        techtree.set_node_level(self._tree_type, node_id, 0)
        node_model = techtree.get_node(self._tree_type, node_id)
        assert node_model is not None
        return node_model

    @Slot(int)
    def performUpgradeStart(self, node_id: int) -> None:
        techtree = self._player.player_techtree_model
        if techtree.is_any_node_research_in_progress(self._player):
            return
        if self._other_research_in_progress(self._tree_type, node_id):
            return

        position_library = self._player.game_config.tech_tree_position_library
        tree_data = position_library.get(self._tree_type)
        if tree_data is None:
            return

        node_info = None
        for candidate in tree_data.get("Nodes", []):
            if int(candidate["Id"]) == node_id:
                node_info = candidate
                break
        if node_info is None:
            return

        try:
            if not techtree.node_requirements_met(self._player, self._tree_type, node_id):
                return
        except ValueError:
            return

        node_model = self._ensure_node(node_id)
        tier = int(node_info.get("Tier", 0))
        internal_level = node_model.level
        try:
            node_type = TechTreeNodeType[node_info["Type"]]
        except KeyError:
            return
        level_max = self._level_max(node_type)
        if node_model.level + 1 >= level_max:
            return

        upgrade_info = lookup_upgrade_level_info(
            self._player.game_config,
            tier,
            internal_level,
        )
        if upgrade_info is None:
            return
        upgrade_cost, duration_seconds = upgrade_info

        affordable, spend_context = can_afford(
            self._player,
            CurrencyType.TechPotions,
            upgrade_cost,
        )
        if not affordable or spend_context is None:
            return

        spend_context.spend("TechTreeNodeUpgradeStart")
        now = self._player.get_server_time()
        duration = int(duration_seconds)
        node_model.node_upgrade_timer_model = TimerModel(
            start_time=now,
            end_time=now + duration,
            duration=float(duration),
        )
        self.refresh()

    @Slot(int)
    def performGemSkip(self, node_id: int) -> None:
        node_model = self._player.player_techtree_model.get_node(self._tree_type, node_id)
        if node_model is None:
            return
        timer = node_model.node_upgrade_timer_model
        if timer.end_time <= timer.start_time or timer.has_ended(self._player):
            return

        gem_cost = timer.calculate_gem_skip_cost(self._player, GemSkipTarget.TechTree)
        affordable, spend_context = can_afford(
            self._player,
            CurrencyType.Gems,
            gem_cost,
        )
        if not affordable or spend_context is None:
            return

        spend_context.spend("TechTreeNodeUpgradeGemSkip")
        timer.skip_to_end(self._player)
        self.refresh()

    @Slot(int)
    def performUpgradeClaim(self, node_id: int) -> None:
        node_model = self._player.player_techtree_model.get_node(self._tree_type, node_id)
        if node_model is None:
            return
        timer = node_model.node_upgrade_timer_model
        if timer.end_time <= timer.start_time or not timer.has_ended(self._player):
            return

        techtree = self._player.player_techtree_model
        techtree.set_node_level(self._tree_type, node_id, node_model.level + 1)
        node_model.node_upgrade_timer_model = TimerModel(
            start_time=0,
            end_time=0,
            duration=0,
        )
        self.refresh()

    @Property(int, notify=changed)
    def treeType(self) -> int:
        return int(self._tree_type.value)

    @Property(float, notify=changed)
    def progress(self) -> float:
        return self._progress

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
