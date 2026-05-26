from __future__ import annotations

import uuid
from dataclasses import dataclass, field

from cli.domain.history import SummonHistory


@dataclass
class Session:
    player: object
    game_logic: object
    dump_raw: str = ""
    history: SummonHistory = field(default_factory=SummonHistory)
    pet_registry: object | None = None
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    db: object | None = None
