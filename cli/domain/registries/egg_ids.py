from __future__ import annotations

import re

from core.game_logic.player_model.EggModel import EggModel

EGG_ID_RE = re.compile(r"^Egg_([0-9A-Fa-f]{3})$", re.IGNORECASE)


def egg_id_from_seed(seed: int) -> str:
    suffix = f"{seed & 0xFFFFFFFFFFFFFFFF:016X}"[-3:].upper()
    return f"Egg_{suffix}"


def egg_id_for(egg: EggModel) -> str:
    return egg_id_from_seed(egg.seed)


def egg_id_suffix(egg_id: str) -> str:
    if egg_id.upper().startswith("EGG_"):
        return egg_id.split("_", 1)[-1].upper()
    return egg_id


def parse_egg_id(token: str) -> str | None:
    m = EGG_ID_RE.match(token.strip())
    return f"Egg_{m.group(1).upper()}" if m else None
