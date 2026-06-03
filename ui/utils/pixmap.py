from __future__ import annotations

from pathlib import Path

from PySide6.QtGui import QPixmap

_cache: dict[str, QPixmap] = {}


def load_pixmap(path: str | Path) -> QPixmap:
	"""Load an image from disk. Requires QGuiApplication."""
	file_path = Path(path)
	if not file_path.is_file():
		return QPixmap()
	return QPixmap(str(file_path.resolve()))


def load_pixmap_cached(path: str | Path) -> QPixmap:
	key = str(Path(path).resolve())
	if key not in _cache:
		_cache[key] = load_pixmap(path)
	return _cache[key]
