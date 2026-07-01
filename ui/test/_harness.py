from pathlib import Path

from app.harness import (
	create_app_engine,
	default_window_size,
	load_qml,
	set_window_context,
)
from utils.paths import project_root

DUMP_PATH = project_root() / "ui" / "test" / "fixtures" / "test_user_dump.txt"

__all__ = [
	"DUMP_PATH",
	"create_app_engine",
	"default_window_size",
	"load_qml",
	"set_window_context",
]
