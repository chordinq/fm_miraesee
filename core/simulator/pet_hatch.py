"""
ONLY FOR REFERENCE — disabled until game_logic APIs are migrated.
Re-enable by uncommenting the block below.
"""

# from __future__ import annotations
#
# from dataclasses import dataclass
# from typing import TYPE_CHECKING
#
# from config import PET_LIBRARY, PETS_MAPPING, SECONDARY_STAT_PET_UNLOCK
# from core.enums import AscensionLevel, Rarity
# from core.random_pcg import RandomPCG
# from core.game_logic.player_model import EggModel
# from core.game_logic.secondary_stats import SecondaryStats
# from core.game_logic.stat_helper import SecondaryStatHelper
#
# if TYPE_CHECKING:
# 	from core.game_logic.player_model import PlayerModel
#
# @dataclass
# class HatchPrediction:
# 	egg_seed:        int
# 	rarity:          Rarity
# 	pet_name:        str
# 	pet_idx:         int
# 	secondary_stats: SecondaryStats
#
# def _build_pets_by_rarity() -> dict[str, list[dict]]:
# 	pools: dict[str, list[dict]] = {r.name: [] for r in Rarity}
# 	for data in PET_LIBRARY.values():
# 		rarity_name = data["PetId"]["Rarity"]
# 		if rarity_name in pools:
# 			pools[rarity_name].append(data)
# 	return pools
#
# _PETS_BY_RARITY: dict[str, list[dict]] = _build_pets_by_rarity()
#
# _PET_STAT_COUNT: dict[str, int] = {
# 	k: v["NumberOfSecondStats"] for k, v in SECONDARY_STAT_PET_UNLOCK.items()
# }
#
# _UNLOCK_BY_RARITY_ORDER: list[dict] = list(SECONDARY_STAT_PET_UNLOCK.values())
#
# def _secondary_stat_count(player: "PlayerModel | None", pet_rarity: Rarity) -> int:
# 	if player is not None and player.pets.ascension_model.current_level >= AscensionLevel.Mega:
# 		if _UNLOCK_BY_RARITY_ORDER:
# 			return _UNLOCK_BY_RARITY_ORDER[-1]["NumberOfSecondStats"]
# 		return 1
# 	return _PET_STAT_COUNT.get(pet_rarity.name, 1)
#
# def predict_hatch(egg: EggModel, player: "PlayerModel | None" = None) -> HatchPrediction:
# 	rng  = RandomPCG(egg.seed)
# 	pool = _PETS_BY_RARITY[egg.rarity.name]
# 	if not pool:
# 		raise ValueError(f"No pets found for rarity {egg.rarity.name}")
#
# 	chosen = pool[rng.next_int(len(pool))]
# 	pet_id = chosen["PetId"]["Id"]
#
# 	rng.next_guid()
#
# 	stat_count = _secondary_stat_count(player, egg.rarity)
# 	secondary  = SecondaryStatHelper.generate_secondary_stats(stat_count, rng)
#
# 	rarity_val = egg.rarity.value
# 	pet_name   = next(
# 		(v["Key"] for v in PETS_MAPPING.values()
# 		 if v.get("Rarity") == rarity_val and v.get("Idx") == pet_id),
# 		f"Pet#{pet_id}",
# 	)
#
# 	return HatchPrediction(
# 		egg_seed=egg.seed,
# 		rarity=egg.rarity,
# 		pet_name=pet_name,
# 		pet_idx=pet_id,
# 		secondary_stats=secondary,
# 	)
