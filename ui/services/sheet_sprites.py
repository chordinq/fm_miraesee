# ui/services/sheet_sprites.py — atlas crops from ManualSpriteMapping + assets/Textures
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPixmap

from configs.config import MANUAL_SPRITE_MAPPING
from core.enums import Rarity
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.services.item_sprites import texture_search_dirs
from ui.services.pixmap_util import dpr_cache_key, pixel_size, pixmap_device_pixels, scale_pixmap_smooth

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


def atlas_pixmap(
    category: str,
    index: int,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    tile = _crop_atlas(category, index)
    if tile is None or tile.isNull():
        return None
    return scale_pixmap_smooth(
        tile,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
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


def skill_icon_pixmap(
    skill: SkillModel,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    idx = _skill_index_by_name().get(skill.combat_skill.name)
    if idx is None:
        return None
    return atlas_pixmap(
        "skills",
        idx,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
    )


def egg_icon_pixmap(
    egg: EggModel,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    rarity_val = int(getattr(egg.rarity, "value", egg.rarity))
    idx = _egg_index_by_rarity().get(rarity_val)
    if idx is None:
        return None
    return atlas_pixmap(
        "eggs",
        idx,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
    )


def pet_icon_pixmap(
    pet: PetModel,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    idx = _pet_index_by_key().get((int(pet.rarity), int(pet.pet_id)))
    if idx is None:
        return None
    return atlas_pixmap(
        "pets",
        idx,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
    )


def mount_icon_pixmap(
    mount: MountModel,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    idx = _mount_index_by_key().get((int(mount.rarity), int(mount.mount_id)))
    if idx is None:
        return None
    return atlas_pixmap(
        "mounts",
        idx,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
    )


_SMALL_ROUND_BUTTON = "SmallRoundButton.png"
_CIRCLE_OUTLINE = "Circle_Outline.png"


def _scale_square(pix: QPixmap, pixel_size: int) -> QPixmap:
    return pix.scaled(
        pixel_size,
        pixel_size,
        Qt.AspectRatioMode.IgnoreAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )


def _argb_pixmap(width: int, height: int | None = None) -> QPixmap:
    """Pixmap with a real alpha channel (plain QPixmap.fill loses transparency)."""
    h = height if height is not None else width
    image = QImage(width, h, QImage.Format.Format_ARGB32)
    image.fill(0)
    return QPixmap.fromImage(image)


@lru_cache(maxsize=1)
def _small_round_button_source() -> QPixmap | None:
    path = texture_path(_SMALL_ROUND_BUTTON)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


@lru_cache(maxsize=1)
def _circle_outline_source() -> QPixmap | None:
    path = texture_path(_CIRCLE_OUTLINE)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


def multiply_tint_pixmap(base: QPixmap, color_hex: str) -> QPixmap:
    """Tint a white/grey plate while preserving built-in shading (Multiply)."""
    if base.isNull():
        return base
    base = pixmap_device_pixels(base)
    w, h = base.width(), base.height()
    color_layer = _argb_pixmap(w, h)
    color_painter = QPainter(color_layer)
    color_painter.fillRect(color_layer.rect(), QColor(color_hex))
    color_painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    color_painter.drawPixmap(0, 0, base)
    color_painter.end()

    result = _argb_pixmap(w, h)
    painter = QPainter(result)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    painter.drawPixmap(0, 0, base)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Multiply)
    painter.drawPixmap(0, 0, color_layer)
    painter.end()
    return result


def _masked_color_pixmap(mask: QPixmap, color_hex: str) -> QPixmap:
    mask = pixmap_device_pixels(mask)
    layer = _argb_pixmap(mask.width(), mask.height())
    painter = QPainter(layer)
    painter.fillRect(layer.rect(), QColor(color_hex))
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_DestinationIn)
    painter.drawPixmap(0, 0, mask)
    painter.end()
    return layer


@lru_cache(maxsize=256)
def skill_disc_plate_pixmap(
    logical_size: int,
    color_hex: str,
    device_pixel_ratio_key: int,
) -> QPixmap | None:
    device_pixel_ratio = device_pixel_ratio_key / 100.0
    source = _small_round_button_source()
    if source is None:
        return None
    px = pixel_size(logical_size, device_pixel_ratio)
    return multiply_tint_pixmap(_scale_square(source, px), color_hex)


@lru_cache(maxsize=64)
def skill_disc_ring_pixmap(
    logical_size: int,
    ring_color_hex: str,
    device_pixel_ratio_key: int,
) -> QPixmap | None:
    device_pixel_ratio = device_pixel_ratio_key / 100.0
    source = _circle_outline_source()
    if source is None:
        return None
    px = pixel_size(logical_size, device_pixel_ratio)
    return _masked_color_pixmap(_scale_square(source, px), ring_color_hex)


