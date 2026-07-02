"""IL: MountVisualConfig.GetMountName, GameContextExtensions.GetName(MountId)."""
from __future__ import annotations

from core.game_logic.enums import Rarity

from .localizer import format_bracketed_entity_title
from .localizer_base import get_translation


def get_mount_name(name_key: str, *, language: str | None = None) -> str:
	"""IL: MountVisualConfig.GetMountName."""
	return get_translation(name_key, table="Mounts", language=language)


def get_mount_display_name(
	name_key: str,
	rarity: Rarity,
	*,
	language: str | None = None,
) -> str:
	"""IL: GameContextExtensions.GetName(MountId)."""
	return format_bracketed_entity_title(
		rarity,
		get_mount_name(name_key, language=language),
		language=language,
	)
