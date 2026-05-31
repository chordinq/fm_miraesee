# core/game_logic/summon_cost.py — tech-reduced summon ticket cost (Skill / Mount)
from __future__ import annotations

from typing import TYPE_CHECKING

from config import TECH_TREE_LIBRARY
from core.enums import TechTreeNodeType
from core.game_logic.summon_config import SummonConfig

if TYPE_CHECKING:
    from core.game_logic.player_model.PlayerModel import PlayerModel

_SUMMON_COST_NODE_KEY: dict[TechTreeNodeType, str] = {
    TechTreeNodeType.SkillSummonCost: "SkillSummonCost",
    TechTreeNodeType.MountSummonCost: "MountSummonCost",
}


def summon_cost_multiplier(player: "PlayerModel | None", node_type: TechTreeNodeType) -> float:
    """
    TechTreeLibrary OneMinusMultiplier on Cost: 1 − (UI levels × ValueIncrease).

    SkillSummonCost / MountSummonCost: ValueIncrease ≈ 1 % per level.
    """
    if player is None:
        return 1.0
    key = _SUMMON_COST_NODE_KEY.get(node_type)
    if key is None:
        return 1.0
    lib_entry = TECH_TREE_LIBRARY.get(key)
    if not lib_entry or not lib_entry.get("Stats"):
        return 1.0
    stat_row = lib_entry["Stats"][0]
    per_level = float(stat_row.get("ValueIncrease", stat_row.get("Value", 0.0)))
    levels = player.get_tech_level(node_type)
    return max(0.0, 1.0 - levels * per_level)


def effective_batch_ticket_cost(
    player: "PlayerModel",
    config: SummonConfig,
    node_type: TechTreeNodeType,
    batch_size: int,
) -> int:
    """Tickets for one summon action of ``batch_size`` pulls (after tech discount)."""
    base = config.cost_per_summon * batch_size
    mult = summon_cost_multiplier(player, node_type)
    return max(0, int(round(base * mult)))


def can_afford_summon_batch(
    player: "PlayerModel",
    config: SummonConfig,
    node_type: TechTreeNodeType,
    batch_size: int,
) -> bool:
    return player.get_currency(config.currency_type) >= effective_batch_ticket_cost(
        player, config, node_type, batch_size
    )


def spend_summon_batch(
    player: "PlayerModel",
    config: SummonConfig,
    node_type: TechTreeNodeType,
    batch_size: int,
) -> int:
    """Deduct discounted ticket cost; returns amount spent."""
    cost = effective_batch_ticket_cost(player, config, node_type, batch_size)
    player.sub_currency(config.currency_type, cost)
    return cost
