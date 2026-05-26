from __future__ import annotations

from core.game_logic.pet_egg_hatch import predict_hatch
from cli.domain.registries.pet_grid import ensure_registry, hatch_slot_eggs, all_eggs, resolve_egg_target


def predict_all(session, target: str = "") -> list:
    reg = ensure_registry(session)
    if target.lower() == "all":
        pairs = all_eggs(session.player.pets)
    elif target:
        egg = resolve_egg_target(reg, target)
        pairs = [(None, egg)] if egg else []
    else:
        pairs = hatch_slot_eggs(reg)
    return [predict_hatch(egg) for _, egg in pairs if egg]
