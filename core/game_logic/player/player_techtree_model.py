from __future__ import annotations
from typing import TYPE_CHECKING
from ..enums import TechTreeNodeType, TechTreeType
from ..stats import Stats
from ..stats.stat_helper import StatHelper
from .timer_model import TimerModel

if TYPE_CHECKING:
	from .player_model import PlayerModel

_MAX_NODE_LEVEL = 4


class TechTreeNodeModel:
	def __init__(self, level: int = 0) -> None:
		self.level = level
		self.node_upgrade_timer_model = TimerModel(
			start_time=0,
			end_time=0,
			duration=0,
		)


def _find_position_node(tree_data: dict, node_id: int) -> dict | None:
	nodes = tree_data.get("Nodes", [])
	if 0 <= node_id < len(nodes) and nodes[node_id].get("Id") == node_id:
		return nodes[node_id]
	for node in nodes:
		if node.get("Id") == node_id:
			return node
	return None


def _tier_addition_value(lib_entry: dict, tier: int) -> float:
	tier_additions = lib_entry.get("TierAddition") or []
	if tier < 0 or tier >= len(tier_additions):
		return 0.0
	return float(tier_additions[tier])


def _stat_value_at_level(row: dict, level: int, tier_bonus: float) -> float:
	return (
		float(row.get("Value", 0.0))
		+ float(row.get("ValueIncrease", 0.0)) * level
		+ tier_bonus
	)


class PlayerTechTreeModel:
	def __init__(self) -> None:
		self.tech_trees: dict[TechTreeType, dict[int, TechTreeNodeModel]] = {
			tree_type: {} for tree_type in TechTreeType
		}

	def set_node_level(
		self,
		tree_type: TechTreeType,
		node_id: int,
		level: int,
	) -> None:
		if level < -1:
			self.tech_trees[tree_type].pop(node_id, None)
			return
		clamped = min(max(level, -1), _MAX_NODE_LEVEL)
		existing = self.tech_trees[tree_type].get(node_id)
		if existing is not None:
			existing.level = clamped
			return
		self.tech_trees[tree_type][node_id] = TechTreeNodeModel(level=clamped)

	def get_node(
		self,
		tree_type: TechTreeType,
		node_id: int,
	) -> TechTreeNodeModel | None:
		return self.tech_trees.get(tree_type, {}).get(node_id)

	def get_total_stats(self, player: PlayerModel) -> Stats:
		game_config = player.game_config
		result = Stats()
		position_library = game_config.tech_tree_position_library
		node_library = game_config.tech_tree_library

		for tree_type, nodes in self.tech_trees.items():
			tree_data = position_library.get(tree_type)
			if tree_data is None:
				continue
			for node_id, node_model in nodes.items():
				if node_model.level < 0:
					continue
				node_info = _find_position_node(tree_data, node_id)
				if node_info is None:
					continue
				try:
					node_type = TechTreeNodeType[node_info["Type"]]
				except KeyError:
					continue
				lib_entry = node_library.get(node_type)
				if lib_entry is None:
					continue
				tier_bonus = _tier_addition_value(
					lib_entry, int(node_info.get("Tier", 0))
				)
				for row in lib_entry.get("Stats", []):
					value = _stat_value_at_level(row, node_model.level, tier_bonus)
					stat_node = StatHelper.parse_stat_node(row["StatNode"])
					result.add_stat_contribution(stat_node, value)
		return result

	def node_requirements_met(
		self,
		player: PlayerModel,
		tree_type: TechTreeType,
		node_id: int,
	) -> bool:
		game_config = player.game_config
		tree_data = game_config.tech_tree_position_library.get(tree_type)
		if tree_data is None:
			raise ValueError(f"Unknown tech tree type: {tree_type!r}")
		node_info = _find_position_node(tree_data, node_id)
		if node_info is None:
			raise ValueError(f"Unknown node id {node_id} for {tree_type!r}")
		tree_nodes = self.tech_trees.get(tree_type, {})
		for req_id in node_info.get("Requirements", []):
			if req_id not in tree_nodes:
				return False
		return True

	def is_any_node_research_in_progress(self, player: PlayerModel) -> bool:
		for nodes in self.tech_trees.values():
			for node_model in nodes.values():
				timer = node_model.node_upgrade_timer_model
				if timer.end_time > timer.start_time and not timer.has_ended(player):
					return True
		return False

	def try_get_claimable_nodes(
		self,
		player: PlayerModel,
	) -> tuple[bool, set[tuple[TechTreeType, int]]]:
		claimable: set[tuple[TechTreeType, int]] = set()
		for tree_type, nodes in self.tech_trees.items():
			for node_id, node_model in nodes.items():
				timer = node_model.node_upgrade_timer_model
				if timer.end_time > timer.start_time and timer.has_ended(player):
					claimable.add((tree_type, node_id))
		return len(claimable) > 0, claimable

	def any_node_complete(self, player: PlayerModel) -> bool:
		for nodes in self.tech_trees.values():
			for node_model in nodes.values():
				timer = node_model.node_upgrade_timer_model
				if timer.end_time > timer.start_time and timer.has_ended(player):
					return True
		return False

	def get_tech_tree_progress(
		self,
		player: PlayerModel,
		tree_type: TechTreeType,
	) -> float:
		game_config = player.game_config
		tree_data = game_config.tech_tree_position_library.get(tree_type)
		if tree_data is None:
			raise ValueError(f"Unknown tech tree type: {tree_type!r}")

		node_library = game_config.tech_tree_library
		max_level_sum = 0
		for node_info in tree_data.get("Nodes", []):
			try:
				node_type = TechTreeNodeType[node_info["Type"]]
			except KeyError:
				continue
			lib_entry = node_library.get(node_type)
			if lib_entry is None:
				continue
			max_level_sum += int(lib_entry.get("MaxLevel", 0))

		if max_level_sum < 1:
			return 0.0

		player_nodes = self.tech_trees.get(tree_type, {})
		level_sum = sum(node.level + 1 for node in player_nodes.values())
		return float(level_sum) / float(max_level_sum)
