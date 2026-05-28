# ui/views/collection/footer_placement.py
from __future__ import annotations

from enum import Enum


class FooterPlacement(Enum):
    NONE = "none"
    IN_PANEL = "in_panel"
    FULL_WIDTH = "full_width"
