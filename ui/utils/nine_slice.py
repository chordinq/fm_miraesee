from __future__ import annotations

from PySide6.QtGui import QPixmap

# TODO: scale UI chrome (buttons, popups) via 9-slice margins.


def nine_slice(
	source: QPixmap,
	margins: tuple[int, int, int, int],
	target_size: tuple[int, int],
) -> QPixmap:
	raise NotImplementedError("nine_slice — planned for button/popup chrome")
