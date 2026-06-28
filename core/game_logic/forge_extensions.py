from __future__ import annotations

from typing import TYPE_CHECKING

from .enums import StatType
from .stats.stat_helper import StatHelper
from .stats.stat_target import ForgeStatTarget

if TYPE_CHECKING:
	from .player.player_model import PlayerModel


def get_forge_tier_upgrade_cost(player: PlayerModel) -> int:
	"""IL: ForgeExtensions.GetForgeTierUpgradeCost."""
	forge = player.player_forge_model
	if forge.forge_tiers_maxed(player):
		return 0
	if forge.forge_levels_maxed(player):
		return 0

	upgrade_row = player.game_config.forge_upgrade_library.get(forge.forge_level + 1)
	if upgrade_row is None:
		raise ValueError(
			f"No ForgeUpgradeLibrary entry for level {forge.forge_level + 1}"
		)

	tiers = int(upgrade_row.get("Tiers", 0))
	cost = int(upgrade_row.get("Cost", 0))
	base_cost = cost // tiers if tiers != 0 else 0
	value = StatHelper.calculate_value(
		player,
		StatType.Cost,
		ForgeStatTarget(),
		base_cost,
	)
	return round(value)
