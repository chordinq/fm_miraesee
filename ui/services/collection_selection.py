# ui/services/collection_selection.py — clicked collection / equipment item
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from core.enums import ItemType
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.SkillModel import SkillModel

SelectionKind = Literal["pet", "egg", "mount", "skill", "equipment", "empty"]


@dataclass(frozen=True)
class CollectionSelection:
    kind: SelectionKind
    pet: PetModel | None = None
    egg: EggModel | None = None
    mount: MountModel | None = None
    skill: SkillModel | None = None
    item: ItemModel | None = None
    slot_type: ItemType | None = None

    @staticmethod
    def empty() -> CollectionSelection:
        return CollectionSelection(kind="empty")
