from __future__ import annotations

from configs import SKILL_SUMMON_CONFIG
from cli.domain.display_names import display_name
from cli.render.collection_grid import CollectionCell, render_collection
from cli.render.summon_bar import format_summon_header


def render(session) -> list[str]:
    skills = session.player.skills
    sm = skills.summon_model
    cfg = SKILL_SUMMON_CONFIG.get_level_config(sm.level)
    lines = [
        format_summon_header(
            "SKILL",
            level=sm.level,
            count=sm.count,
            required=cfg.summons_required,
            ascension_level=skills.ascension_model.current_level,
        ),
        "",
    ]
    ordered = sorted(skills.skills.values(), key=lambda s: (not s.is_equipped, -s.rarity.value))
    cells: list[CollectionCell] = []
    for s in ordered:
        name = display_name(s.name)
        if s.is_equipped:
            name = f"{name}*"
        cells.append(CollectionCell(name=name, subtitle=f"Lv.{s.level + 1}", rarity=s.rarity.value))
    lines.extend(render_collection(cells))
    return lines
