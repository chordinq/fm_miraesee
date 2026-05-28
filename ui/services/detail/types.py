from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from PySide6.QtGui import QPixmap

from ui.services.stat_display import StatLine

DETAIL_ICON_SIZE = 64

DetailIconKind = Literal["skill", "pet", "mount", "equipment"]


@dataclass
class DetailContent:
    title: str
    subtitle: str = ""
    level_text: str = ""
    pixmap: QPixmap | None = None
    frame_color: str = "#4db84a"
    icon_kind: DetailIconKind = "pet"
    title_color: str = "#5DFF8A"
    equipped: bool = False
    stat_lines: list[StatLine] | None = None
    hint: str = ""
    is_hatch_preview: bool = False
    level_color: str = ""
