# config/paths.py
from __future__ import annotations

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

# Depth 1 — direct children of PROJECT_ROOT
CONFIG_DIR = PROJECT_ROOT / "config"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Depth 2 — one segment under ASSETS_DIR (verified on disk)
GAME_CONFIGS_DIR = ASSETS_DIR / "game_configs"
LOCALIZATIONS_DIR = ASSETS_DIR / "localizations"
SPRITES_DIR = ASSETS_DIR / "sprites"
