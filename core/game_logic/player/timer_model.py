from __future__ import annotations

import math
from typing import TYPE_CHECKING

from ..enums import GemSkipTarget

if TYPE_CHECKING:
	from .player_model import PlayerModel


class TimerModel:
	"""Offline sim timer — IL fields: StartTime, EndTime, Duration (seconds)."""

	def __init__(
		self,
		player: PlayerModel | None = None,
		duration_seconds: float = 0,
		*,
		start_time: int | None = None,
		end_time: int | None = None,
		duration: float | None = None,
	) -> None:
		if start_time is not None and end_time is not None:
			self.start_time = start_time
			self.end_time = end_time
			self.duration = float(duration if duration is not None else end_time - start_time)
			return
		if player is None:
			raise ValueError("TimerModel requires player for IL Setup path")
		now = player.get_server_time()
		self.start_time = now
		self.duration = float(duration_seconds)
		self.end_time = now + int(self.duration)

	def has_ended(self, player: PlayerModel) -> bool:
		"""IL: TimerModel.HasEnded — EndTime <= ServerTime."""
		return self.end_time <= player.get_server_time()

	def is_in_progress(self, player: PlayerModel) -> bool:
		"""IL: TimerModel.IsInProgress — EndTime > ServerTime."""
		return self.end_time > player.get_server_time()

	def calculate_remaining_seconds(self, player: PlayerModel) -> int:
		"""IL: TimerModel.CalculateRemainingSeconds — EndTime−ServerTime, FloorToInt."""
		return max(0, math.floor(self.end_time - player.get_server_time()))

	def calculate_gem_skip_cost(
		self,
		player: PlayerModel,
		target: GemSkipTarget = GemSkipTarget.Forge,
	) -> int:
		"""IL: TimerModel.CalculateGemSkipCost."""
		remaining = self.calculate_remaining_seconds(player)
		cost_per_second = player.game_config.forge_config.get_gem_skip_cost_per_second(
			target
		)
		return max(1, round(remaining * cost_per_second))

	def skip_to_end(self, player: PlayerModel) -> None:
		"""IL: TimerModel.SkipToEnd — EndTime = ServerTime."""
		self.end_time = player.get_server_time()

	def skip(self, seconds: int) -> None:
		"""IL: TimerModel.Skip — EndTime -= duration."""
		self.end_time = max(self.start_time, self.end_time - seconds)

	def get_progress(self, player: PlayerModel) -> float:
		"""IL: TimerModel.GetProgress."""
		if self.has_ended(player):
			return 0.0
		if self.duration <= 0:
			return 1.0
		remaining = self.calculate_remaining_seconds(player)
		return 1.0 - remaining / self.duration
