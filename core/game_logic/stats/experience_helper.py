from __future__ import annotations

from typing import Any


def _level_info_entries(upgrade_config: dict[str, Any]) -> list[dict[str, Any]]:
	level_info = upgrade_config.get("LevelInfo")
	if level_info is None:
		raise ValueError("Missing LevelInfo on upgrade config")
	return level_info


def total_level_xp(level_info: list[dict[str, Any]], level: int) -> int:
	if level < 0:
		return 0
	total = 0
	for i in range(min(level + 1, len(level_info))):
		entry = level_info[i]
		if entry is None:
			raise ValueError(f"Missing level entry at index {i}")
		total += int(entry["Experience"])
	return total


def calculate_level_and_xp(level_info: list[dict[str, Any]], total_xp: int) -> tuple[int, int]:
	current_level = 0
	remaining = total_xp
	for entry in level_info:
		if entry is None:
			raise ValueError("Missing level entry in upgrade config")
		cost = int(entry["Experience"])
		if remaining - cost < 0:
			break
		remaining -= cost
		current_level = int(entry["Level"])
	return current_level, remaining


def first_level_experience(level_info: list[dict[str, Any]]) -> int:
	if not level_info:
		raise IndexError("Upgrade config has no level entries")
	first = level_info[0]
	if first is None:
		raise ValueError("Missing first level entry")
	return int(first["Experience"])
