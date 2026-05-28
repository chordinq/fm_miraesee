# ui/services/detail_content.py — shim → ui.services.detail
from ui.services.detail import (
    DetailContent,
    DetailIconKind,
    content_for_selection,
)
from ui.services.detail.types import DETAIL_ICON_SIZE

__all__ = [
    "DETAIL_ICON_SIZE",
    "DetailContent",
    "DetailIconKind",
    "content_for_selection",
]
