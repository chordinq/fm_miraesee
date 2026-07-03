"""PyInstaller runtime hook — fix DPI before Qt or splash handoff."""
from __future__ import annotations

import ctypes
import os
import sys

os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")
os.environ.setdefault("QT_SCALE_FACTOR", "1")

if sys.platform == "win32":
	try:
		ctypes.windll.shcore.SetProcessDpiAwareness(1)
	except Exception:
		try:
			ctypes.windll.user32.SetProcessDPIAware()
		except Exception:
			pass
