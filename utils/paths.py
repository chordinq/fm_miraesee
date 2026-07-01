"""Project root resolution (dev tree + PyInstaller onedir exe)."""
from __future__ import annotations

import sys
from pathlib import Path


def is_frozen() -> bool:
	return getattr(sys, "frozen", False)


def install_dir() -> Path:
	if is_frozen():
		return Path(sys.executable).resolve().parent
	return Path(__file__).resolve().parents[1]


def bundle_dir() -> Path:
	if is_frozen():
		return Path(getattr(sys, "_MEIPASS", install_dir()))
	return install_dir()


def assets_dir() -> Path:
	external = install_dir() / "assets"
	if external.is_dir():
		return external
	return bundle_dir() / "assets"


def project_root() -> Path:
	return bundle_dir()


def data_dir() -> Path:
	return install_dir() / "data"
