from __future__ import annotations

from core.game_logic.player_model.PlayerModel import PlayerModel

from ui.services.collection_selection import CollectionSelection
from ui.services.detail.builders import (
    content_for_egg,
    content_for_item,
    content_for_mount,
    content_for_pet,
    content_for_skill,
)
from ui.services.detail.types import DetailContent


def content_for_selection(
    sel: CollectionSelection,
    player: PlayerModel | None = None,
) -> DetailContent | None:
    if sel.kind == "empty":
        return None
    if sel.kind == "pet" and sel.pet is not None:
        return content_for_pet(sel.pet, player)
    if sel.kind == "egg" and sel.egg is not None:
        return content_for_egg(sel.egg, player)
    if sel.kind == "mount" and sel.mount is not None:
        return content_for_mount(sel.mount)
    if sel.kind == "skill" and sel.skill is not None:
        return content_for_skill(sel.skill)
    if sel.kind == "equipment" and sel.item is not None:
        return content_for_item(sel.item)
    return None
