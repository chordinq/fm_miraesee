from __future__ import annotations

import re
from dataclasses import dataclass, field

from cli.domain.registries.egg_ids import egg_id_for, parse_egg_id
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.PetModel import PetModel

_GRID_COLS = 5
_HATCH_SLOT_COUNT = 4
_GRID_RE = re.compile(r"^(\d+)([A-Ea-e])$", re.IGNORECASE)
_HATCH_RE = re.compile(r"^H([1-4])$", re.IGNORECASE)


@dataclass
class GridCell:
    kind: str
    pet: PetModel | None = None
    egg: EggModel | None = None
    egg_id: str | None = None
    grid_pos: str | None = None


@dataclass
class PetCollectionRegistry:
    grid: list[GridCell] = field(default_factory=list)
    by_id: dict[str, EggModel] = field(default_factory=dict)
    by_grid: dict[str, EggModel] = field(default_factory=dict)
    hatch_alias: dict[str, str] = field(default_factory=dict)


def _fifo_by_rarity(items: list) -> list:
    """Stable rarity descending — preserves dump / acquisition order within a tier."""
    return sorted(enumerate(items), key=lambda x: (-x[1].rarity.value, x[0]))


def sorted_collection_pets(pets: list[PetModel]) -> list[PetModel]:
    """Equipped by slot, then unequipped in dump FIFO order (higher rarity first)."""
    equipped = sorted([p for p in pets if p.is_equipped], key=lambda p: p.equip_slot)
    unequipped = [p for _, p in _fifo_by_rarity([p for p in pets if not p.is_equipped])]
    return equipped + unequipped


def sorted_inventory_eggs(eggs: list[EggModel]) -> list[EggModel]:
    """Non-hatch inventory eggs in dump FIFO order (higher rarity first)."""
    inv = [e for e in eggs if not e.is_equipped]
    return [e for _, e in _fifo_by_rarity(inv)]


def _col_letter(col: int) -> str:
    return chr(ord("A") + col)


def build_registry(pets_model) -> PetCollectionRegistry:
    reg = PetCollectionRegistry()
    grid_i = 0
    for pet in sorted_collection_pets(pets_model.pets):
        row, col = divmod(grid_i, _GRID_COLS)
        reg.grid.append(GridCell(kind="pet", pet=pet, grid_pos=f"{row + 1}{_col_letter(col)}"))
        grid_i += 1
    for egg in sorted_inventory_eggs(pets_model.eggs):
        eid = egg_id_for(egg)
        row, col = divmod(grid_i, _GRID_COLS)
        pos = f"{row + 1}{_col_letter(col)}"
        reg.grid.append(GridCell(kind="egg", egg=egg, egg_id=eid, grid_pos=pos))
        reg.by_id[eid] = egg
        reg.by_grid[pos.upper()] = egg
        grid_i += 1
    for slot in range(_HATCH_SLOT_COUNT):
        egg = next((e for e in pets_model.eggs if e.is_equipped and e.equip_slot == slot), None)
        if egg is None:
            continue
        eid = egg_id_for(egg)
        hid = f"H{slot + 1}"
        reg.by_id[eid] = egg
        reg.by_id[hid] = egg
        reg.hatch_alias[hid] = eid
    return reg


def ensure_registry(session) -> PetCollectionRegistry:
    reg = build_registry(session.player.pets)
    session.pet_registry = reg
    return reg


def resolve_egg_target(reg: PetCollectionRegistry, token: str) -> EggModel | None:
    t = token.strip()
    norm = parse_egg_id(t)
    if norm:
        return reg.by_id.get(norm)
    m = _HATCH_RE.match(t.upper())
    if m:
        return reg.by_id.get(f"H{int(m.group(1))}")
    m = _GRID_RE.match(t.upper())
    if m:
        return reg.by_grid.get(f"{int(m.group(1))}{m.group(2).upper()}")
    return None


def hatch_slot_eggs(reg: PetCollectionRegistry) -> list[tuple[str, EggModel]]:
    out, seen = [], set()
    for slot in range(_HATCH_SLOT_COUNT):
        hid = f"H{slot + 1}"
        egg = reg.by_id.get(hid)
        if egg is None or egg.seed in seen:
            continue
        seen.add(egg.seed)
        out.append((reg.hatch_alias.get(hid, egg_id_for(egg)), egg))
    return out


def all_eggs(pets_model) -> list[tuple[str, EggModel]]:
    return sorted([(egg_id_for(e), e) for e in pets_model.eggs], key=lambda x: x[0])
