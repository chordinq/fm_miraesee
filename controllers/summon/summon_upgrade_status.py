from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
	from core.game_logic.player.summon_model import SummonModel
	from core.game_logic.config.summon_config import SummonConfig


def read_summon_upgrade_status(
	summon_model: SummonModel,
	summon_config: SummonConfig,
) -> dict[str, int | float | bool]:
	level = summon_model.level
	count = summon_model.count
	next_idx = level + 1
	if next_idx < len(summon_config.levels):
		required = summon_config.levels[next_idx].summons_required
		is_maxed = False
		fraction = count / required if required > 0 else 0.0
	else:
		required = max(count, 1)
		is_maxed = True
		fraction = 1.0
	return {
		"summonLevel": level + 1,
		"progressCount": count,
		"progressRequired": required,
		"progressFraction": min(1.0, max(0.0, fraction)),
		"isMaxed": is_maxed,
	}
