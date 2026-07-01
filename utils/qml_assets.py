"""Link bundled _internal/assets to install_dir/assets for QML relative paths."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from utils.paths import bundle_dir, install_dir, is_frozen


def ensure_internal_assets_link() -> None:
	if not is_frozen():
		return
	external = install_dir() / "assets"
	if not external.is_dir():
		return
	internal = bundle_dir() / "assets"
	if internal.exists():
		return
	internal.parent.mkdir(parents=True, exist_ok=True)
	if sys.platform == "win32":
		result = subprocess.run(
			["cmd", "/c", "mklink", "/J", str(internal), str(external.resolve())],
			capture_output=True,
			text=True,
			creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
		)
		if result.returncode != 0:
			raise RuntimeError(
				f"failed to link assets into bundle: {result.stderr.strip() or result.stdout.strip()}"
			)
		return
	os.symlink(external.resolve(), internal, target_is_directory=True)
