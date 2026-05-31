# ui/utils/ImageHelper.py — mount/pet sprite sheets from mapping JSON
from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QRect
from PySide6.QtGui import QPixmap

from config import MOUNTS_MAPPING, PETS_MAPPING, SPRITES_DIR
from core.enums import AscensionLevel, Rarity

_MOUNT_ICONS_DIR = SPRITES_DIR / "Mount"
MOUNT_COLS = 4
MOUNT_ICON_SIZE = 256


class ImageHelper:
	_sprite_sheets: dict[str, QPixmap] = {}
	_mount_data: dict = {}
	_pet_data: dict = {}

	@classmethod
	def load_mappings(cls) -> None:
		cls._mount_data = MOUNTS_MAPPING
		cls._pet_data = PETS_MAPPING

	@classmethod
	def mount_sheet_path(cls, ascension_level: AscensionLevel) -> Path:
		if ascension_level == AscensionLevel.None_:
			return _MOUNT_ICONS_DIR / "None_MountIcons.png"
		return _MOUNT_ICONS_DIR / f"{ascension_level.name}MountIcons.png"

	@classmethod
	def get_sprite(cls, file_path: str | Path, crop_rect: QRect) -> QPixmap:
		path = Path(file_path)
		key = str(path.resolve())
		if key not in cls._sprite_sheets:
			if not path.is_file():
				return QPixmap()
			cls._sprite_sheets[key] = QPixmap(str(path))
		return cls._sprite_sheets[key].copy(crop_rect)

	@classmethod
	def get_mount_sprite(
		cls,
		rarity: Rarity,
		idx: int,
		ascension_level: AscensionLevel = AscensionLevel.None_,
	) -> QPixmap:
		dict_key = f"{rarity.value}_{idx}"
		if dict_key not in cls._mount_data:
			return QPixmap()

		pos_idx = cls._mount_data[dict_key]["Sprite"]["Idx"]
		file_path = cls.mount_sheet_path(ascension_level)

		x = (pos_idx % MOUNT_COLS) * MOUNT_ICON_SIZE
		y = (pos_idx // MOUNT_COLS) * MOUNT_ICON_SIZE
		sprite_pos = QRect(x, y, MOUNT_ICON_SIZE, MOUNT_ICON_SIZE)
		return cls.get_sprite(file_path, sprite_pos)
