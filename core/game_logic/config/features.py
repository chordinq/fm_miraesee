"""IL: Features static segment lists and Features.FeatureId / Features.IsUnlocked."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..enums import AscendableType

if TYPE_CHECKING:
	from ..player.player_model import PlayerModel

SKILL_SLOTS: tuple[str, ...] = ("SkillSlot0", "SkillSlot1", "SkillSlot2")
PET_SLOTS: tuple[str, ...] = ("PetSlot0", "PetSlot1", "PetSlot2")

ASCENSION_FEATURE_IDS: dict[AscendableType, str] = {
	AscendableType.Forge: "ForgeAscension",
	AscendableType.Mounts: "MountsAscension",
	AscendableType.Pets: "PetsAscension",
	AscendableType.Skills: "SkillsAscension",
}


def feature_id(ascendable_type: AscendableType) -> str:
	"""IL: Features.FeatureId."""
	segment_id = ASCENSION_FEATURE_IDS.get(ascendable_type)
	if segment_id is None:
		raise ValueError(f"Features.FeatureId: unknown AscendableType {ascendable_type!r}")
	return segment_id


def is_unlocked(ascendable_type: AscendableType, player: PlayerModel) -> bool:
	"""IL: Features.IsUnlocked."""
	from ..unlock_extensions import is_unlocked as is_segment_unlocked

	return is_segment_unlocked(feature_id(ascendable_type), player)
