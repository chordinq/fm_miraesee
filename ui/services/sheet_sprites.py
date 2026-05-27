# ui/services/sheet_sprites.py — atlas crops from ManualSpriteMapping + assets/Textures
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from configs.config import MANUAL_SPRITE_MAPPING
from core.enums import Rarity
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.services.item_sprites import texture_search_dirs

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]
_CATEGORIES = ("skills", "pets", "mounts", "eggs")


def texture_path(filename: str) -> Path | None:
    for directory in texture_search_dirs():
        direct = directory / filename
        if direct.is_file():
            return direct
    for root_name in ("assets", "Assets"):
        candidate = _SCRIPTS_ROOT / root_name / "Textures" / filename
        if candidate.is_file():
            return candidate
    return None


def texture_pixmap(
    filename: str,
    width: int,
    height: int | None = None,
) -> QPixmap | None:
    """Load a standalone texture from assets/Textures and scale."""
    path = texture_path(filename)
    if path is None:
        return None
    pix = QPixmap(str(path))
    if pix.isNull():
        return None
    h = height if height is not None else width
    return pix.scaled(
        width,
        h,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def _texture_path(filename: str) -> Path | None:
    return texture_path(filename)


@lru_cache(maxsize=8)
def _load_sheet(category: str) -> QPixmap | None:
    if category not in _CATEGORIES:
        return None
    meta = MANUAL_SPRITE_MAPPING.get(category)
    if not meta:
        return None
    path = _texture_path(str(meta["texture"]))
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


def _crop_atlas(category: str, index: int) -> QPixmap | None:
    sheet = _load_sheet(category)
    meta = MANUAL_SPRITE_MAPPING.get(category)
    if sheet is None or meta is None:
        return None
    sw = int(meta["sprite_size"]["width"])
    sh = int(meta["sprite_size"]["height"])
    cols = int(meta["grid"]["columns"])
    col = index % cols
    row = index // cols
    return sheet.copy(col * sw, row * sh, sw, sh)


def atlas_pixmap(category: str, index: int, size: int) -> QPixmap | None:
    tile = _crop_atlas(category, index)
    if tile is None or tile.isNull():
        return None
    return tile.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


@lru_cache
def _skill_index_by_name() -> dict[str, int]:
    """Atlas index by CombatSkill member name (grid slot), not enum_value field."""
    out: dict[str, int] = {}
    for idx, entry in MANUAL_SPRITE_MAPPING["skills"]["mapping"].items():
        out[str(entry["name"])] = int(idx)
    return out


@lru_cache
def _pet_index_by_key() -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = {}
    for idx, entry in MANUAL_SPRITE_MAPPING["pets"]["mapping"].items():
        rarity = Rarity[entry["rarity"]].value
        out[(rarity, int(entry["id"]))] = int(idx)
    return out


@lru_cache
def _egg_index_by_rarity() -> dict[int, int]:
    out: dict[int, int] = {}
    for idx, entry in MANUAL_SPRITE_MAPPING["eggs"]["mapping"].items():
        rarity = Rarity[entry["rarity"]].value
        out[rarity] = int(idx)
    return out


@lru_cache
def _mount_index_by_key() -> dict[tuple[int, int], int]:
    out: dict[tuple[int, int], int] = {}
    for idx, entry in MANUAL_SPRITE_MAPPING["mounts"]["mapping"].items():
        rarity = Rarity[entry["rarity"]].value
        out[(rarity, int(entry["id"]))] = int(idx)
    return out


def skill_icon_pixmap(skill: SkillModel, size: int) -> QPixmap | None:
    idx = _skill_index_by_name().get(skill.combat_skill.name)
    if idx is None:
        return None
    return atlas_pixmap("skills", idx, size)


def egg_icon_pixmap(egg: EggModel, size: int) -> QPixmap | None:
    idx = _egg_index_by_rarity().get(int(egg.rarity))
    if idx is None:
        return None
    return atlas_pixmap("eggs", idx, size)


def pet_icon_pixmap(pet: PetModel, size: int) -> QPixmap | None:
    idx = _pet_index_by_key().get((int(pet.rarity), int(pet.pet_id)))
    if idx is None:
        return None
    return atlas_pixmap("pets", idx, size)


def mount_icon_pixmap(mount: MountModel, size: int) -> QPixmap | None:
    idx = _mount_index_by_key().get((int(mount.rarity), int(mount.mount_id)))
    if idx is None:
        return None
    return atlas_pixmap("mounts", idx, size)
