"""Manual sprite preview — not production UI.

From ``scripts/`` (after ``pip install -e .``):
  python sprite_preview.py
  python -m ui.tests.sprite_preview
"""
from __future__ import annotations

import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
	QApplication,
	QHBoxLayout,
	QLabel,
	QVBoxLayout,
	QWidget,
)

from core.enums import AscendableType, AscensionLevel, Rarity
from ui.components.sprites import (
	get_item_sprite,
	get_mount_sprite,
	get_pet_sprite,
	get_skill_sprite,
)
from ui.utils import SpriteLoader

_ICON = 256

_RARITY_SAMPLES: tuple[tuple[Rarity, int], ...] = (
	(Rarity.Common, 1),
	(Rarity.Rare, 0),
	(Rarity.Ultimate, 1),
	(Rarity.Mythic, 0),
)

_ITEM_KEYS = ("0_0_0", "1_5_5", "4_5_0", "9_5_5")

_ASCENDABLE_ROWS: tuple[tuple[str, AscendableType, type], ...] = (
	("Mounts", AscendableType.Mounts, get_mount_sprite),
	("Pets", AscendableType.Pets, get_pet_sprite),
	("Skills", AscendableType.Skills, get_skill_sprite),
)


def _caption(kind: AscendableType, mapping_key: str, *, rarity: Rarity | None = None) -> str:
	entry = SpriteLoader.mapping_for(kind).get(mapping_key)
	name = entry.get("Key", "?") if entry else "?"
	if rarity is None:
		return name
	return f"{rarity.name} {name}"


def _row(layout: QVBoxLayout, title: str, pixmaps: list[tuple[str, QPixmap]]) -> None:
	layout.addWidget(QLabel(f"<b>{title}</b>"))
	row = QHBoxLayout()
	for caption, pixmap in pixmaps:
		col = QVBoxLayout()
		col.addWidget(QLabel(caption))
		img = QLabel()
		img.setPixmap(pixmap)
		img.setFixedSize(_ICON, _ICON)
		col.addWidget(img)
		row.addLayout(col)
	layout.addLayout(row)


def run() -> None: 
	app = QApplication(sys.argv)
	asc = AscensionLevel.None_

	win = QWidget()
	layout = QVBoxLayout()

	for title, kind, get_sprite in _ASCENDABLE_ROWS:
		samples = [
			(
				_caption(kind, SpriteLoader.rarity_idx_key(rarity, idx), rarity=rarity),
				get_sprite(rarity, idx, asc),
			)
			for rarity, idx in _RARITY_SAMPLES
		]
		_row(layout, title, samples)

	items = [
		(
			_caption(AscendableType.Forge, key),
			get_item_sprite(key, asc),
		)
		for key in _ITEM_KEYS
	]
	_row(layout, "Items (Equipment)", items)

	win.setLayout(layout)
	win.setWindowTitle("Sprite Preview (test)")
	win.resize(4 * (_ICON + 40), 4 * (_ICON + 60))
	win.show()
	sys.exit(app.exec())


if __name__ == "__main__":
	run()
