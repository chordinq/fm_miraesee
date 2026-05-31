# ui/app.py — Qt entry (mount sprite test window)
from __future__ import annotations

import sys

from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from core.enums import AscensionLevel, Rarity
from ui.utils.ImageHelper import ImageHelper


def run() -> None:
    """Launch the mount sprite test window."""
    ImageHelper.load_mappings()

    mount_examples = [
        (Rarity.Common, 0, AscensionLevel.None_),  # LilyPad
        (Rarity.Rare, 3, AscensionLevel.None_),  # Turtle
        (Rarity.Ultimate, 1, AscensionLevel.None_),  # MiniDragon
        (Rarity.Mythic, 1, AscensionLevel.None_),  # HoverBoard
    ]

    app = QApplication(sys.argv)
    win = QWidget()
    layout = QVBoxLayout()

    for rarity, idx, ascension in mount_examples:
        pixmap: QPixmap = ImageHelper.get_mount_sprite(rarity, idx, ascension)
        label = QLabel()
        label.setPixmap(pixmap)
        label.setFixedSize(256, 256)
        layout.addWidget(label)

    win.setLayout(layout)
    win.setWindowTitle("Mount Sprite Test")
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    run()
