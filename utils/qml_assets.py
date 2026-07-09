"""Link bundled _internal/assets to install_dir/assets for QML relative paths."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from utils.paths import bundle_dir, install_dir, is_frozen


def _path_entry_exists(path: Path) -> bool:
	try:
		path.lstat()
		return True
	except OSError:
		return False


def _link_target_matches(link: Path, target: Path) -> bool:
	try:
		return link.is_dir() and link.resolve() == target.resolve()
	except OSError:
		return False


def _remove_link(path: Path) -> None:
	if not _path_entry_exists(path):
		return
	if sys.platform == "win32":
		result = subprocess.run(
			["cmd", "/c", "rmdir", str(path)],
			capture_output=True,
			text=True,
			creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
		)
		if result.returncode != 0:
			raise RuntimeError(
				f"failed to remove assets link: {result.stderr.strip() or result.stdout.strip()}"
			)
		return
	path.unlink()


def _create_link(link: Path, target: Path) -> None:
	link.parent.mkdir(parents=True, exist_ok=True)
	if sys.platform == "win32":
		result = subprocess.run(
			["cmd", "/c", "mklink", "/J", str(link), str(target)],
			capture_output=True,
			text=True,
			creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
		)
		if result.returncode == 0:
			return
		message = result.stderr.strip() or result.stdout.strip()
		if _path_entry_exists(link) and _link_target_matches(link, target):
			return
		if _path_entry_exists(link):
			_remove_link(link)
			retry = subprocess.run(
				["cmd", "/c", "mklink", "/J", str(link), str(target)],
				capture_output=True,
				text=True,
				creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
			)
			if retry.returncode == 0 or (
				_path_entry_exists(link) and _link_target_matches(link, target)
			):
				return
			message = retry.stderr.strip() or retry.stdout.strip()
		raise RuntimeError(f"failed to link assets into bundle: {message}")
	try:
		link.symlink_to(target, target_is_directory=True)
	except FileExistsError:
		if not _link_target_matches(link, target):
			_remove_link(link)
			link.symlink_to(target, target_is_directory=True)


def ensure_internal_assets_link() -> None:
	if not is_frozen():
		return
	external = install_dir() / "assets"
	if not external.is_dir():
		return
	internal = bundle_dir() / "assets"
	target = external.resolve()
	if _path_entry_exists(internal):
		if _link_target_matches(internal, target):
			return
		_remove_link(internal)
	_create_link(internal, target)
