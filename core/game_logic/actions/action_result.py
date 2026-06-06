from __future__ import annotations


class MetaActionResult:
	__slots__ = ("name",)

	def __init__(self, name: str) -> None:
		self.name = name

	def __eq__(self, other: object) -> bool:
		if isinstance(other, MetaActionResult):
			return self is other
		return NotImplemented

	def __hash__(self) -> int:
		return id(self)

	def __repr__(self) -> str:
		return f"ActionResult.{self.name}"


class ActionResult:
	Success = MetaActionResult("Success")
	NoCheatsAllowed = MetaActionResult("NoCheatsAllowed")
	UnknownError = MetaActionResult("UnknownError")
	NotEnoughResources = MetaActionResult("NotEnoughResources")
	LevelTooLow = MetaActionResult("LevelTooLow")
	AlreadyInProgress = MetaActionResult("AlreadyInProgress")
	NotStarted = MetaActionResult("NotStarted")
	NotReady = MetaActionResult("NotReady")
	NoMainBattle = MetaActionResult("NoMainBattle")
	NotFinished = MetaActionResult("NotFinished")
	DoesNotExist = MetaActionResult("DoesNotExist")
	NoItems = MetaActionResult("NoItems")
	MaxLevelReached = MetaActionResult("MaxLevelReached")
	NoCombat = MetaActionResult("NoCombat")
	AlreadyEquipped = MetaActionResult("AlreadyEquipped")
	AlreadyUnequipped = MetaActionResult("AlreadyUnequipped")
	NotEquipped = MetaActionResult("NotEquipped")
	DoesNotMakeSense = MetaActionResult("DoesNotMakeSense")
	NotAllowed = MetaActionResult("NotAllowed")
	Locked = MetaActionResult("Locked")
	AlreadyClaimed = MetaActionResult("AlreadyClaimed")
	AlreadyFinished = MetaActionResult("AlreadyFinished")
	HatchingSlotUnavailable = MetaActionResult("HatchingSlotUnavailable")
	BadWord = MetaActionResult("BadWord")
	NameAlreadyTaken = MetaActionResult("NameAlreadyTaken")
	Failure = MetaActionResult("Failure")
	Timeout = MetaActionResult("Timeout")
