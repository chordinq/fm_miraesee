class TimerModel:
	def __init__(self, start_time: int, end_time: int, duration: int) -> None:
		self.start_time = start_time
		self.end_time = end_time
		self.duration = duration

	def has_ended(self, player=None) -> bool:
		_ = player
		return self.end_time <= self.start_time
