# ui/services/collection_entries.py — build grid rows for skill / pet / mount tabs
from __future__ import annotations

from dataclasses import dataclass

from core.enums import Rarity
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.constants.colors import RARITY_BORDER, RARITY_FRAME, TAB_BORDER
from ui.constants.layout import (
    COLLECTION_ICON_SIZE,
    EGG_ICON_SIZE,
    EGG_ICON_TOP_MARGIN,
    EGG_TILE_H,
    EGG_TILE_W,
    FRAME_SIZE,
    FRAME_SPRITE_SIZE,
    SKILL_ICON_SIZE,
)
from PySide6.QtGui import QPixmap

from ui.services.display_level import format_level
from ui.services.skill_shards import shard_progress_label
from ui.services.sheet_sprites import egg_icon_pixmap, mount_icon_pixmap, pet_icon_pixmap, skill_icon_pixmap


@dataclass(frozen=True)
class CollectionTileData:
    meta: str
    border_color: str
    pixmap: QPixmap | None = None
    name: str = ""
    frame_color: str | None = None
    equipped: bool = False
    framed: bool = False
    icon_size: int | None = None
    icon_area_h: int | None = None
    icon_top_margin: int | None = None
    tile_w: int | None = None
    tile_h: int | None = None
    circular: bool = False
    shard_label: str = ""


def _rarity_border(rarity: Rarity) -> str:
    return RARITY_BORDER.get(int(rarity), TAB_BORDER)


def _rarity_frame(rarity: Rarity) -> str:
    return RARITY_FRAME.get(int(rarity), TAB_BORDER)


def skill_entries(player: PlayerModel) -> list[CollectionTileData]:
    skills = list(player.skills.skills.values())
    # Common → Mythic, then CombatSkill enum order (not idx, not equipped).
    skills.sort(key=lambda s: (int(s.rarity), int(s.combat_skill)))
    rows: list[CollectionTileData] = []
    for skill in skills:
        rows.append(
            CollectionTileData(
                meta=format_level(skill.level),
                border_color=_rarity_border(skill.rarity),
                frame_color=_rarity_frame(skill.rarity),
                pixmap=skill_icon_pixmap(skill, SKILL_ICON_SIZE),
                equipped=skill.is_equipped,
                circular=True,
                shard_label=shard_progress_label(skill),
            )
        )
    return rows


def pet_entries(player: PlayerModel) -> list[CollectionTileData]:
    rows: list[CollectionTileData] = []
    for entry in player.pets.tolist(include_eggs=True):
        if entry["type"] == "Egg":
            egg: EggModel = entry["obj"]
            rows.append(
                CollectionTileData(
                    name="",
                    meta="Egg",
                    border_color=_rarity_border(egg.rarity),
                    pixmap=egg_icon_pixmap(egg, EGG_ICON_SIZE),
                    icon_size=EGG_ICON_SIZE,
                    icon_area_h=FRAME_SIZE,
                    icon_top_margin=EGG_ICON_TOP_MARGIN,
                    tile_w=EGG_TILE_W,
                    tile_h=EGG_TILE_H,
                )
            )
            continue
        pet: PetModel = entry["obj"]
        rows.append(
            CollectionTileData(
                meta=format_level(pet.level),
                border_color=_rarity_border(pet.rarity),
                frame_color=_rarity_frame(pet.rarity),
                pixmap=pet_icon_pixmap(pet, FRAME_SPRITE_SIZE),
                equipped=pet.is_equipped,
                framed=True,
            )
        )
    return rows


def mount_entries(player: PlayerModel) -> list[CollectionTileData]:
    rows: list[CollectionTileData] = []
    for entry in player.mounts.tolist():
        mount: MountModel = entry["obj"]
        rows.append(
            CollectionTileData(
                meta=format_level(mount.level),
                border_color=_rarity_border(mount.rarity),
                frame_color=_rarity_frame(mount.rarity),
                pixmap=mount_icon_pixmap(mount, FRAME_SPRITE_SIZE),
                equipped=mount.is_equipped,
                framed=True,
            )
        )
    return rows
