from cli.domain.registries.egg_ids import egg_id_for, egg_id_from_seed, parse_egg_id
from cli.domain.registries.pet_grid import (
    ensure_registry, resolve_egg_target, hatch_slot_eggs, all_eggs,
    _GRID_COLS, _HATCH_SLOT_COUNT,
)
