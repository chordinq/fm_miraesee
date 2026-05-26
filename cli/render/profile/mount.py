from __future__ import annotations

from configs import MOUNT_SUMMON_CONFIG, MOUNT_MAPPING
from cli.domain.display_names import display_name
from cli.render.collection_grid import CollectionCell, render_collection
from cli.render.summon_bar import format_summon_header


def render(session) -> list[str]:
    mounts = session.player.mounts
    mm = mounts.summon_model
    cfg = MOUNT_SUMMON_CONFIG.get_level_config(mm.level)
    lines = [
        format_summon_header(
            "MOUNT",
            level=mm.level,
            count=mm.count,
            required=cfg.summons_required,
            ascension_level=mounts.ascension_model.current_level,
        ),
        "",
    ]
    cells: list[CollectionCell] = []
    for m in sorted(mounts.mounts, key=lambda x: (not x.is_equipped, -x.rarity.value)):
        key = f"{m.rarity.value}_{getattr(m, 'mount_id', 0)}"
        name = display_name(MOUNT_MAPPING.get(key, {}).get("Name", "?"))
        if m.is_equipped:
            name = f"{name}*"
        cells.append(CollectionCell(name=name, subtitle=f"Lv.{m.level + 1}", rarity=m.rarity.value))
    lines.extend(render_collection(cells))
    return lines
