# models/TechTreeModel.py
from configs.enums import TechTreeNodeType

class TechTreeModel:
	def __init__(self):
		self.type_totals = {n_type: 0 for n_type in TechTreeNodeType}
		self.nodes = {n_type: {} for n_type in TechTreeNodeType}

	def node_level_inc(self, node_type: TechTreeNodeType, tier: int, amount: int = 1) -> int:
		current_level = self.nodes[node_type].get(tier, 0)
		new_level = current_level + amount
		
		if new_level < 0:
			new_level = 0
		elif new_level > 4:
			new_level = 4
			
		actual_diff = new_level - current_level
		self.nodes[node_type][tier] = new_level
		self.type_totals[node_type] += actual_diff
		
		return new_level

	def set_node_level(self, node_type: TechTreeNodeType, tier: int, level: int):
		current_level = self.nodes[node_type].get(tier, 0)
		self.node_level_inc(node_type, tier, level - current_level)