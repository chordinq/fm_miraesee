from __future__ import annotations

from configs import EGG_SUMMON_CONFIG, PET_MAPPING
from cli.domain.display_names import display_name
from cli.domain.registries.egg_ids import egg_id_suffix
from cli.domain.registries.pet_grid import ensure_registry, _HATCH_SLOT_COUNT
from cli.render.collection_grid import CollectionCell, render_collection
from cli.render.summon_bar import format_summon_header
from cli.theme import BOLD, RESET


def render(session) -> list[str]:
    pets = session.player.pets
    pm = pets.summon_model
    cfg = EGG_SUMMON_CONFIG.get_level_config(pm.level)
    reg = ensure_registry(session)
    lines = [
        format_summon_header(
            "PET/EGG",
            level=pm.level,
            count=pm.count,
            required=cfg.summons_required,
            ascension_level=pets.ascension_model.current_level,
        ),
        "",
    ]
    cells: list[CollectionCell] = []
    for cell in reg.grid:
        if cell.kind == "pet" and cell.pet:
            key = f"{cell.pet.rarity.value}_{cell.pet.pet_id}"
            name = display_name(PET_MAPPING.get(key, {}).get("Name", "?"))
            cells.append(CollectionCell(name=name, subtitle=f"Lv.{cell.pet.level + 1}", rarity=cell.pet.rarity.value))
        elif cell.kind == "egg" and cell.egg_id:
            cells.append(CollectionCell(
                name="Egg",
                subtitle=f"ID:{egg_id_suffix(cell.egg_id)}",
                rarity=cell.egg.rarity.value,
            ))
    lines.extend(render_collection(cells))

    hatch_cells: list[CollectionCell] = []
    for slot in range(_HATCH_SLOT_COUNT):
        hid = f"H{slot + 1}"
        egg = reg.by_id.get(hid)
        if egg:
            eid = reg.hatch_alias.get(hid, "")
            hatch_cells.append(CollectionCell(
                name=f"{hid} Egg",
                subtitle=f"ID:{egg_id_suffix(eid)}",
                rarity=egg.rarity.value,
            ))
        else:
            hatch_cells.append(CollectionCell(name=hid, subtitle="empty", rarity=0))

    lines += ["", f"  {BOLD}Hatch slots{RESET}", ""]
    lines.extend(render_collection(hatch_cells, title=""))
    return lines
