"""IL: ItemAgeDropChanceInfo.GetForgeDropChances + ForgeAction.RollAge."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from ..random_pcg import RandomPCG

if TYPE_CHECKING:
	from .player.player_model import PlayerModel


_AGE_FIELD_NAMES = tuple(f"Age{i}" for i in range(10))


def get_forge_drop_chances(drop_row: dict[str, Any]) -> list[float]:
	"""IL: ItemAgeDropChanceInfo.GetForgeDropChances — Age0..Age9 in order."""
	return [float(drop_row[name]) for name in _AGE_FIELD_NAMES]


def roll_age(player: PlayerModel, rng: RandomPCG) -> int:
	"""IL: ForgeAction.RollAge — cumulative Age0..Age9 vs NextF64."""
	forge = player.player_forge_model
	game_config = player.game_config
	forge_level = forge.forge_level
	drop_row = game_config.item_age_drop_chances_library.get(forge_level)
	if drop_row is None:
		raise ValueError(f"No ItemAgeDropChanceInfo for forge level {forge_level}")

	chances = get_forge_drop_chances(drop_row)
	if not chances:
		return 0

	roll = rng.next_f64()
	accumulated = 0.0
	for index, chance in enumerate(chances):
		accumulated += chance
		if roll < accumulated:
			return index
	return 0
