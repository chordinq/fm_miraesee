from __future__ import annotations

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
from core.format.format_time import format_hatch_duration
from core.format.localizer_base import get_localized
from controllers.models.pet_model_bridge import build_pet_stat_lines
from ui.utils.localizer import rarity_loc_from_rarity

_DEFAULT_LANGUAGE = "en"
_HATCH_DESC_LOC_ID = "153364393984"
_HATCH_DESC_LOC_TABLE = "Pets"


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
	return get_localized(loc_id, table=loc_table, language=language)


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
	hatch_desc_args = [
		format_hatch_duration(duration_seconds, language),
		localized_rarity_name(rarity_value, language),
	]
	preview: dict[str, object] = {
		"predictedPetIndex": -1,
		"predictedPetRarity": rarity_value,
		"hatchDescFormatArgs": hatch_desc_args,
		"hatchDescText": get_localized(
			_HATCH_DESC_LOC_ID,
			table=_HATCH_DESC_LOC_TABLE,
			language=language,
			args=hatch_desc_args,
		),
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
