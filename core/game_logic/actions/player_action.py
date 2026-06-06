from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, ClassVar
from .action_result import MetaActionResult

if TYPE_CHECKING:
	from ..player.player_model import PlayerModel


class PlayerAction(ABC):
	action_code: ClassVar[int | None] = None
	finalized_action_code: ClassVar[int | None] = None

	def __init__(self) -> None:
		pass

	@abstractmethod
	def execute(self, player: PlayerModel, commit: bool = True) -> MetaActionResult:
		raise NotImplementedError
