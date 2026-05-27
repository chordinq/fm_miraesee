# ui/services/item_sprites.py — equipment icons from AutoItemMapping + assets/Textures
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from configs.config import AUTO_ITEM_MAPPING
from core.game_logic.player_model.ItemModel import ItemModel
from ui.services.item_display import item_mapping_key

_SCRIPTS_ROOT = Path(__file__).resolve().parents[2]


@lru_cache
def texture_search_dirs() -> tuple[Path, ...]:
    """Directories to search for per-sprite PNG files (SpriteName.png)."""
    dirs: list[Path] = []
    for root_name in ("assets", "Assets"):
        tex_root = _SCRIPTS_ROOT / root_name / "Textures"
        if not tex_root.is_dir():
            continue
        pub = tex_root / "public" / "Texture2D"
        if pub.is_dir():
            for sub in sorted(pub.iterdir()):
                if sub.is_dir():
                    dirs.append(sub)
        dirs.append(tex_root)
    return tuple(dirs)


def sprite_name_for_item(item: ItemModel) -> str | None:
    key = item_mapping_key(item.age, item.item_type, item.idx)
    entry = AUTO_ITEM_MAPPING.get(key)
    if not entry:
        return None
    name = entry.get("SpriteName")
    return str(name) if name else None


def _find_sprite_path(sprite_name: str) -> Path | None:
    stem = sprite_name.strip()
    if not stem:
        return None
    lower = stem.lower()
    for directory in texture_search_dirs():
        direct = directory / f"{stem}.png"
        if direct.is_file():
            return direct
        try:
            for path in directory.iterdir():
                if path.suffix.lower() == ".png" and path.stem.lower() == lower:
                    return path
        except OSError:
            continue
    return None


@lru_cache(maxsize=512)
def _load_sprite_pixmap(sprite_name: str) -> QPixmap | None:
    path = _find_sprite_path(sprite_name)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


def item_icon_pixmap(item: ItemModel, size: int) -> QPixmap | None:
    sprite = sprite_name_for_item(item)
    if not sprite:
        return None
    base = _load_sprite_pixmap(sprite)
    if base is None or base.isNull():
        return None
    return base.scaled(
        size,
        size,
        Qt.AspectRatioMode.KeepAspectRatio,
        Qt.TransformationMode.SmoothTransformation,
    )
