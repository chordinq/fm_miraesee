# core/game_logic/tech_tree_stats.py
"""
Tech-tree stat multipliers from TechTreeLibrary (dump type_totals × ValueIncrease).

PetBonusDamage / PetBonusHealth and MountDamage / MountHealth use
StatNature Multiplier with TechTreeDamage / TechTreeHealth on PetStatTarget /
MountStatTarget.  Parsed dump levels are summed in TechTreeModel.type_totals.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from configs.config import TECH_TREE_LIBRARY
from core.enums import TechTreeNodeType

if TYPE_CHECKING:
	from core.game_logic.player_model.PlayerModel import PlayerModel

# TechTreeLibrary PetBonusDamage / PetBonusHealth: ValueIncrease ≈ 2 % per UI level.
_NODE_CONFIG_KEY: dict[TechTreeNodeType, str] = {
	TechTreeNodeType.PetBonusDamage: "PetBonusDamage",
	TechTreeNodeType.PetBonusHealth: "PetBonusHealth",
	TechTreeNodeType.MountDamage: "MountDamage",
	TechTreeNodeType.MountHealth: "MountHealth",
}


def tech_tree_multiplier(player: "PlayerModel | None", node: TechTreeNodeType) -> float:
	"""
	Multiplier applied to pet/mount base Damage or Health.

	1 + (sum of researched UI levels for this node type) × ValueIncrease
	"""
	if player is None:
		return 1.0
	key = _NODE_CONFIG_KEY.get(node)
	if key is None:
		return 1.0
	lib_entry = TECH_TREE_LIBRARY.get(key)
	if not lib_entry or not lib_entry.get("Stats"):
		return 1.0
	stat_row = lib_entry["Stats"][0]
	per_level = float(stat_row.get("ValueIncrease", stat_row.get("Value", 0.0)))
	levels = player.get_tech_level(node)
	return 1.0 + levels * per_level


def pet_tech_multipliers(player: "PlayerModel | None") -> tuple[float, float]:
	"""Return (damage_mult, health_mult) from PetBonusDamage / PetBonusHealth."""
	return (
		tech_tree_multiplier(player, TechTreeNodeType.PetBonusDamage),
		tech_tree_multiplier(player, TechTreeNodeType.PetBonusHealth),
	)
