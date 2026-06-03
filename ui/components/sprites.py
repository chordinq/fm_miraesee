from __future__ import annotations

from PySide6.QtGui import QPixmap
from core.enums import AscendableType, AscensionLevel, Rarity
from ui.utils.sprite_loader import SpriteLoader


def get_mount_sprite(rarity: Rarity, idx: int, ascension_level: AscensionLevel) -> QPixmap:
	return SpriteLoader.get_pixmap_for(
		AscendableType.Mounts,
		SpriteLoader.rarity_idx_key(rarity, idx),
		ascension=ascension_level,
	)


def get_pet_sprite(rarity: Rarity, idx: int, ascension_level: AscensionLevel) -> QPixmap:
	return SpriteLoader.get_pixmap_for(
		AscendableType.Pets,
		SpriteLoader.rarity_idx_key(rarity, idx),
		ascension=ascension_level,
	)


def get_skill_sprite(rarity: Rarity, idx: int, ascension_level: AscensionLevel) -> QPixmap:
	return SpriteLoader.get_pixmap_for(
		AscendableType.Skills,
		SpriteLoader.rarity_idx_key(rarity, idx),
		ascension=ascension_level,
	)


def get_item_sprite(mapping_key: str, ascension_level: AscensionLevel) -> QPixmap:
	return SpriteLoader.get_pixmap_for(
		AscendableType.Forge,
		mapping_key,
		ascension=ascension_level,
	)
