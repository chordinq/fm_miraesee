# features/summon/pet_summon.py — pet egg summon use case
from __future__ import annotations

from configs import EGG_SUMMON_CONFIG
from core.enums import CurrencyType
from core.game_logic.GameLogic import GameLogic
from core.game_logic.summon_base import SummonResult
from core.game_logic.player_model.PlayerModel import PlayerModel
from features.session import Session


def pet_summon_batch_size() -> int:
    counts = list(EGG_SUMMON_CONFIG.possible_summon_count)
    return int(counts[0]) if counts else 1


def pet_summon_cost(player: PlayerModel | None = None) -> int:
    _ = player
    return EGG_SUMMON_CONFIG.cost_per_summon


def pet_summon_currency() -> CurrencyType:
    return EGG_SUMMON_CONFIG.currency_type


def pet_eggshell_balance(player: PlayerModel) -> int:
    return player.get_currency(CurrencyType.Eggshells)


def can_afford_pet_summon(player: PlayerModel) -> bool:
    return pet_eggshell_balance(player) >= pet_summon_cost(player)


def execute_pet_summon(session: Session) -> SummonResult:
    """Run one pet summon batch and mutate player state. Returns the result."""
    gl = GameLogic(session.player)
    return gl.summon_eggs(pet_summon_batch_size())
