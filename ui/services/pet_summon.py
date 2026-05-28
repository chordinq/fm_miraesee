# ui/services/pet_summon.py — pet summon UI display helpers
# Game logic lives in features/summon/pet_summon.py; only display helpers here.
from __future__ import annotations

from features.summon.pet_summon import (  # noqa: F401 (re-export for UI convenience)
    can_afford_pet_summon,
    execute_pet_summon,
    pet_eggshell_balance,
    pet_summon_batch_size,
    pet_summon_cost,
    pet_summon_currency,
)
from ui.services.localization import ui_text


def pet_summon_title(batch: int | None = None) -> str:
    n = batch if batch is not None else pet_summon_batch_size()
    return f"{ui_text('summon')} x{n}"
