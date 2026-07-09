from __future__ import annotations

from core.metaplaymath.f64 import F64, f64_from_raw, f64_ratio

"""IL: PlayerModel.TicksPerSecond (=10) and GameTick dt = F64.Ratio(1, 10)."""

TICKS_PER_SECOND = 10
PLAYER_MODEL_GAME_TICK_RAW = f64_ratio(1, 10)


def player_model_game_tick_seconds() -> float:
	return f64_from_raw(PLAYER_MODEL_GAME_TICK_RAW)


def player_model_game_tick() -> F64:
	return F64.ratio(1, 10)
