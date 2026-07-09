from __future__ import annotations

from config import MOUNTS_MAPPING, SKILLS_MAPPING
from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id


def build_skill_summon_preview(
    summoned,
    player: PlayerModel,
) -> list[dict[str, object]]:
    collection = player.player_skill_collection_model
    ascension_level = int(
        AscensionLevel(collection.ascension_model.current_level).value
    )
    preview: list[dict[str, object]] = []
    for info in summoned:
        skill_id = combat_skill_to_skill_id(info.type)
        key = f"{skill_id.rarity.value}_{skill_id.idx}"
        entry = SKILLS_MAPPING[key]
        preview.append(
            {
                "rarity": entry["Rarity"],
                "index": skill_id.idx,
                "ascensionLevel": ascension_level,
                "isNew": info.is_new,
            }
        )
    return preview


def build_egg_summon_preview(
    summoned,
    player: PlayerModel,
) -> list[dict[str, object]]:
    collection = player.player_pet_collection_model
    ascension_level = int(
        AscensionLevel(collection.ascension_model.current_level).value
    )
    preview: list[dict[str, object]] = []
    for info in summoned:
        egg = info.egg_model
        preview.append(
            {
                "rarity": egg.rarity.value,
                "ascensionLevel": ascension_level,
                "isNew": info.is_new,
            }
        )
    return preview


def build_mount_summon_preview(
    summoned,
    player: PlayerModel,
) -> list[dict[str, object]]:
    collection = player.player_mount_collection_model
    ascension_level = int(
        AscensionLevel(collection.ascension_model.current_level).value
    )
    preview: list[dict[str, object]] = []
    for info in summoned:
        mount = info.mount_model
        key = f"{mount.mount_id.rarity.value}_{mount.mount_id.id}"
        entry = MOUNTS_MAPPING[key]
        preview.append(
            {
                "rarity": entry["Rarity"],
                "index": mount.mount_id.id,
                "ascensionLevel": ascension_level,
                "isNew": info.is_new,
            }
        )
    return preview
