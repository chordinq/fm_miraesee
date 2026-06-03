from __future__ import annotations

from PySide6.QtGui import QFont, QFontDatabase
from PySide6.QtWidgets import QApplication
from pathlib import Path
from config import FONTS_DIR

BALOO_FONT_FILE = FONTS_DIR / "Baloo-Regular.ttf"
NOTO_KR_FILE = FONTS_DIR / "NotoSansKR-Bold.otf"
NOTO_JP_FILE = FONTS_DIR / "NotoSansJP-Bold.otf"
DEFAULT_FONT_SIZE = 14

def apply_font(app: QApplication, *, size: int = DEFAULT_FONT_SIZE) -> str | None:
    font_id_baloo = QFontDatabase.addApplicationFont(str(BALOO_FONT_FILE))
    font_id_kr = QFontDatabase.addApplicationFont(str(NOTO_KR_FILE))
    font_id_jp = QFontDatabase.addApplicationFont(str(NOTO_JP_FILE))

    family_baloo = QFontDatabase.applicationFontFamilies(font_id_baloo)[0]
    family_kr = QFontDatabase.applicationFontFamilies(font_id_kr)[0]
    family_jp = QFontDatabase.applicationFontFamilies(font_id_jp)[0]

    QFont.insertSubstitutions(family_baloo, [family_kr, family_jp])
    app.setFont(QFont(family_baloo, size))

    return family_baloo