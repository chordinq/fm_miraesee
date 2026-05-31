# config/config.py
import json
from pathlib import Path

def load_json(file_path: Path) -> dict:
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_FONT_DIR = _PROJECT_ROOT / "assets" / "fonts"
_GAME_CONFIG_DIR = _PROJECT_ROOT / "assets" / "game"
_LOCALIZATION_DIR = _PROJECT_ROOT / "assets" / "localization"
_SPRITE_DIR = _PROJECT_ROOT / "assets" / "sprites"
