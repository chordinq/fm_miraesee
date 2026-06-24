from __future__ import annotations

from collections import defaultdict

from PySide6.QtCore import QObject, Property, Signal

from config import TECHTREE_MAPPING, TECH_TREE_LIBRARY
from core.game_logic.enums import TechTreeNodeType, TechTreeType
from core.game_logic.player.player_model import PlayerModel


class TechTreeNodeBridge(QObject):
    changed = Signal()

    def __init__(
        self,
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
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
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

    def _node_key(self, node_type: int) -> str:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        return str(entry.get("Key", ""))

    def _sprite_index(self, node_type: int) -> int:
        entry = TECHTREE_MAPPING.get("TechTreeNodeType", {}).get(str(node_type), {})
        sprite = entry.get("Sprite")
        if sprite is None:
            return -1
        return int(sprite["Idx"])

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

    def _icon_level(
        self,
        node_model,
        requirements_met: bool,
    ) -> int:
        if not requirements_met:
            return -2
        if node_model is None:
            return -2
        timer = node_model.node_upgrade_timer_model
        if timer.end_time > timer.start_time and not timer.has_ended(self._player):
            return -1
        return int(node_model.level)

    def _refresh(self) -> None:
        position_library = self._player.game_config.tech_tree_position_library
        tree_data = position_library.get(self._tree_type)
        techtree = self._player.player_techtree_model

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

                    nodes.append(
                        TechTreeNodeBridge(
                            node_type=int(node_type.value),
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
                            node_key=self._node_key(int(node_type.value)),
                            sprite_index=self._sprite_index(int(node_type.value)),
                            parent=self,
                        )
                    )

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
