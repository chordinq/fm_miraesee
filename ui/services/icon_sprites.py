# ui/services/icon_sprites.py — UI icons from Icons.png + IconsMap.json
from __future__ import annotations

from functools import lru_cache

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from configs.config import ICONS_MAP
from core.enums import CurrencyType
from ui.services.pixmap_util import scale_pixmap_smooth
from ui.services.sheet_sprites import texture_path

_ICON_BY_NAME: dict[str, int] = {
    entry["name"]: int(index) for index, entry in ICONS_MAP["mapping"].items()
}

CURRENCY_ICON_NAME: dict[CurrencyType, str] = {
    CurrencyType.Coins: "Coin",
    CurrencyType.Gems: "GemSquare",
    CurrencyType.Hammers: "Hammer",
    CurrencyType.SkillSummonTickets: "SkillTicket",
    CurrencyType.TechPotions: "Potion",
    CurrencyType.PvpTickets: "PVPTicket",
    CurrencyType.ClockWinders: "MountKey",
    CurrencyType.WarBattleTickets: "WarTicket",
    CurrencyType.Eggshells: "Eggshell",
    CurrencyType.MissionEnergy: "Lightning",
    CurrencyType.GuildPotions: "GuildPotions",
}


@lru_cache(maxsize=1)
def _icons_sheet() -> QPixmap | None:
    filename = str(ICONS_MAP.get("texture", "Icons.png"))
    path = texture_path(filename)
    if path is None:
        return None
    pix = QPixmap(str(path))
    return pix if not pix.isNull() else None


def icon_pixmap_by_name(
    name: str,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    """Crop a named icon from Icons.png and scale to *logical_size* at device resolution."""
    index = _ICON_BY_NAME.get(name)
    if index is None:
        return None
    sheet = _icons_sheet()
    if sheet is None:
        return None
    sw = int(ICONS_MAP["sprite_size"]["width"])
    sh = int(ICONS_MAP["sprite_size"]["height"])
    rect = ICONS_MAP["mapping"][str(index)]["sprite_rect"]
    cropped = sheet.copy(int(rect["x"]), int(rect["y"]), sw, sh)
    if cropped.isNull():
        return None
    return scale_pixmap_smooth(
        cropped,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
        keep_aspect=Qt.AspectRatioMode.KeepAspectRatio,
    )


def currency_icon_pixmap(
    currency: CurrencyType,
    logical_size: int,
    *,
    device_pixel_ratio: float = 1.0,
) -> QPixmap | None:
    name = CURRENCY_ICON_NAME.get(currency)
    if name is None:
        return None
    return icon_pixmap_by_name(
        name,
        logical_size,
        device_pixel_ratio=device_pixel_ratio,
    )
