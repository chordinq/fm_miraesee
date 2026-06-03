from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap

from config import (
	ITEMS_MAPPING,
	MOUNTS_MAPPING,
	PETS_MAPPING,
	SKILLS_MAPPING,
	SPRITE_SHEETS,
	SPRITES_DIR,
)
from core.enums import AscendableType, AscensionLevel, Rarity
from .pixmap import load_pixmap_cached

_ATLAS_SPRITE_FILES = frozenset({"MountIcons", "Pets", "SkillIcons"})

_ASCENDABLE_MAPPINGS: dict[AscendableType, dict] = {
	AscendableType.Mounts: MOUNTS_MAPPING,
	AscendableType.Pets: PETS_MAPPING,
	AscendableType.Skills: SKILLS_MAPPING,
}


class SpriteLoader:
	@classmethod
	def mapping_for(cls, kind: AscendableType) -> dict:
		if kind == AscendableType.Forge:
			return ITEMS_MAPPING.get("items", {})
		return _ASCENDABLE_MAPPINGS[kind]

	@classmethod
	def sprite_index(cls, sprite: dict) -> int:
		return int(sprite.get("Idx", sprite.get("Pos", 0)))

	@classmethod
	def sheet_key(cls, sprite: dict, ascension: AscensionLevel) -> str:
		file_name = sprite["File"]
		if file_name in _ATLAS_SPRITE_FILES:
			return f"{ascension.name}{file_name}"
		return file_name

	@classmethod
	def sheet_path(cls, sheet_key: str) -> Path:
		if sheet_key.startswith("Icon"):
			return SPRITES_DIR / "Equipment" / f"{sheet_key}.png"
		if "MountIcons" in sheet_key:
			return SPRITES_DIR / "Mount" / f"{sheet_key}.png"
		if sheet_key.endswith("Pets"):
			return SPRITES_DIR / "Pet" / f"{sheet_key}.png"
		if "SkillIcons" in sheet_key:
			return SPRITES_DIR / "Skill" / f"{sheet_key}.png"
		return SPRITES_DIR / "Equipment" / f"{sheet_key}.png"

	@classmethod
	def get_pixmap(
		cls,
		sprite: dict,
		*,
		ascension: AscensionLevel = AscensionLevel.None_,
	) -> QPixmap:
		key = cls.sheet_key(sprite, ascension)
		meta = SPRITE_SHEETS.get(key)
		if not meta:
			return QPixmap()

		pixmap = load_pixmap_cached(cls.sheet_path(key))
		if pixmap.isNull():
			return QPixmap()

		cols = int(meta["cols"])
		icon_size = int(meta["iconSize"])
		idx = cls.sprite_index(sprite)
		if cols <= 1:
			return pixmap

		x = (idx % cols) * icon_size
		y = (idx // cols) * icon_size
		return pixmap.copy(QRect(x, y, icon_size, icon_size))

	@classmethod
	def get_pixmap_for(
		cls,
		kind: AscendableType,
		mapping_key: str,
		*,
		ascension: AscensionLevel = AscensionLevel.None_,
	) -> QPixmap:
		entry = cls.mapping_for(kind).get(mapping_key)
		if not entry:
			return QPixmap()
		return cls.get_pixmap(entry["Sprite"], ascension=ascension)

	@classmethod
	def rarity_idx_key(cls, rarity: Rarity, idx: int) -> str:
		return f"{rarity.value}_{idx}"
