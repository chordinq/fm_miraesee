# cli/render/equipment.py
"""
Equipment display — swap this file (or EQUIPMENT_RENDERER) for Pillow/images.

Usage:
    from cli.render.equipment import render_equipment
    lines = render_equipment(session)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from cli.render.protocol import EquipmentRenderer

if TYPE_CHECKING:
    pass

# ── Text renderer (default) ───────────────────────────────────────────────────


class TextEquipmentRenderer:
    def render(self, session) -> list[str]:
        from configs import ITEM_MAPPING
        from cli.domain.display_names import display_name
        from cli.domain.stats import fmt_stat_hatch
        from cli.theme import BOLD, C_MUTED, C_WHITE, RESET, age_color
        from core.enums import ItemType, AscensionLevel

        fg = session.player.forge
        eq = session.player.equipment

        def game_level(raw: int) -> int:
            return raw + 1

        def item_name(item) -> str:
            key = f"{item.age.value}_{item.item_type.value}_{item.idx}"
            data = ITEM_MAPPING.get(key)
            return display_name(data.get("Name", f"#{item.idx}")) if data else item.item_type.name

        from cli.render.summon_bar import format_profile_header

        lines: list[str] = [
            format_profile_header("FORGE", level=fg.forge_level),
            f"  {C_MUTED}{'─' * 48}{RESET}",
            "",
            f"  {BOLD}Equipped{RESET}",
            "",
        ]
        labels = {
            ItemType.Helmet: "Helmet", ItemType.Armour: "Armour",
            ItemType.Gloves: "Gloves", ItemType.Necklace: "Necklace",
            ItemType.Ring: "Ring", ItemType.Shoes: "Shoes",
            ItemType.Belt: "Belt", ItemType.Weapon: "Weapon",
        }
        for itype in ItemType:
            item = eq.get_equipped_item(itype)
            label = labels.get(itype, itype.name)
            if item is None:
                lines.append(f"  {C_MUTED}{label:10s}  · empty{RESET}")
                lines.append("")
                continue
            ac = age_color(item.age.value)
            lines.append(
                f"  {C_MUTED}{label:10s}{RESET}  {ac}{BOLD}{item_name(item)}{RESET}"
                f"  {C_MUTED}Lv.{game_level(item.level)}{RESET}"
            )
            for s in item.secondary_stats.stats:
                lines.append("    " + fmt_stat_hatch(s.stat_type.name, s.perfection, 0).strip())
            lines.append("")
        return lines


# Pillow example (stub):
# class PillowEquipmentRenderer:
#     def render(self, session) -> list[str]:
#         from PIL import Image
#         ... build image ...
#         return ["  [equipment image saved to /tmp/gear.png]"]

_RENDERER: EquipmentRenderer = TextEquipmentRenderer()


def render_equipment(session) -> list[str]:
    return _RENDERER.render(session)


def set_equipment_renderer(renderer: EquipmentRenderer) -> None:
    global _RENDERER
    _RENDERER = renderer
