from __future__ import annotations

import json
from pathlib import Path

from core.game_logic.enums import StatType
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import (
    PlayerEggModel,
    PlayerPetModel,
    create_pet_from_ids,
    pet_ids_for_rarity,
)
from core.random_pcg import RandomPCG
from core.game_logic.stats.stat_helper import StatHelper
from core.game_logic.stats.stat_target import EggStatTarget
from ui.utils.localizer import LOCALIZATIONS_DIR, rarity_loc_from_rarity
from ui.utils.pet_stat_display import build_pet_stat_lines
from ui.utils.timer_display import format_hatch_duration, format_timer_duration

_DEFAULT_LANGUAGE = "en"
_LOC_TABLE_CACHE: dict[str, dict[str, str]] = {}


def _load_loc_table(table: str, language: str) -> dict[str, str]:
    cache_key = f"{table}_{language}"
    cached = _LOC_TABLE_CACHE.get(cache_key)
    if cached is not None:
        return cached

    mapping: dict[str, str] = {}
    for lang in (language, _DEFAULT_LANGUAGE):
        path = LOCALIZATIONS_DIR / f"{table}_{lang}.json"
        if not path.exists():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for entry in data.get("m_TableData", []):
                mapping[str(entry["m_Id"])] = entry["m_Localized"]
        except (OSError, KeyError, json.JSONDecodeError, TypeError):
            pass
        if mapping:
            break

    _LOC_TABLE_CACHE[cache_key] = mapping
    return mapping


def _load_loc_string(loc_id: str, table: str, language: str) -> str:
    if not loc_id:
        return ""
    return _load_loc_table(table, language).get(loc_id, "")


def calculate_hatch_duration_seconds(player: PlayerModel, egg: PlayerEggModel) -> int:
    egg_config = player.game_config.egg_library.get(egg.rarity)
    if egg_config is None:
        return 0
    base_duration = float(egg_config.get("HatchTime", 0))
    target = EggStatTarget(egg.rarity)
    return round(
        StatHelper.calculate_value(
            player,
            StatType.TimerSpeed,
            target,
            base_duration,
        )
    )


def localized_rarity_name(rarity: int, language: str = _DEFAULT_LANGUAGE) -> str:
    loc_id, loc_table = rarity_loc_from_rarity(rarity)
    if not loc_id:
        return ""
    return _load_loc_string(loc_id, loc_table, language)


def predict_hatched_pet(player: PlayerModel, egg: PlayerEggModel) -> PlayerPetModel | None:
    pet_ids = pet_ids_for_rarity(player.game_config.pet_library, egg.rarity)
    if not pet_ids:
        return None
    rng = RandomPCG.create_from_seed(egg.random_seed)
    return create_pet_from_ids(player, pet_ids, rng, None)


def build_egg_hatch_preview_meta(
    player: PlayerModel,
    egg: PlayerEggModel,
    *,
    language: str = _DEFAULT_LANGUAGE,
) -> dict[str, object]:
    duration_seconds = calculate_hatch_duration_seconds(player, egg)
    rarity_value = egg.rarity.value
    preview: dict[str, object] = {
        "predictedPetIndex": -1,
        "predictedPetRarity": rarity_value,
        "hatchDescFormatArgs": [
            format_hatch_duration(duration_seconds, language),
            localized_rarity_name(rarity_value, language),
        ],
    }

    pet = predict_hatched_pet(player, egg)
    if pet is None:
        return preview

    preview["predictedPetIndex"] = pet.pet_id.id
    preview["predictedPetRarity"] = pet.pet_id.rarity.value
    return preview


def build_egg_hatch_stat_lines(
    player: PlayerModel,
    egg: PlayerEggModel,
) -> list[dict[str, object]]:
    pet = predict_hatched_pet(player, egg)
    if pet is None:
        return []
    return build_pet_stat_lines(player, pet)


def build_egg_hatch_preview(
    player: PlayerModel,
    egg: PlayerEggModel,
    *,
    language: str = _DEFAULT_LANGUAGE,
) -> dict[str, object]:
    preview = build_egg_hatch_preview_meta(player, egg, language=language)
    preview["statLines"] = build_egg_hatch_stat_lines(player, egg)
    return preview
