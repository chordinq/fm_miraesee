# core/game_logic/pet_egg_hatch.py
"""
Pet egg hatch prediction.

C# PetEggHatchFinalizedAction$$Execute flow:
  1. Filter PetConfig where PetId.Rarity == egg.rarity -> ToList<PetId> (config order)
  2. rng = RandomPCG.CreateFromSeed(egg.seed)   // PlayerEggModel+0x38
  3. PetExtensions.CreatePet(player, pet_id_list, rng):
        Choice<PetId>(list)  -> IList: NextInt(count) + indexer  (1 PCG call)
        CreatePet(player, petId, rng):
          NextGuid()  (4 PCG calls)
          stat_count from SecondaryStatPetUnlockLibrary (see _secondary_stat_count)
          SecondaryStatHelper.GenerateSecondaryStats:
            Choice<SecondaryStatType> per stat  (1 PCG + NextF64 each)

CreateEggModel also calls NextGuid from the same seed at summon time, but hatch
re-initializes PCG from the stored seed, so that does not shift the hatch stream.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from configs import PET_LIBRARY, PET_MAPPING, SECONDARY_STAT_PET_UNLOCK
from core.enums import AscensionLevel, Rarity, RARITY_NAMES
from core.random_pcg import RandomPCG
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.secondary_stats import generate_secondary_stats

if TYPE_CHECKING:
	from core.game_logic.player_model.PlayerModel import PlayerModel


@dataclass
class HatchPrediction:
	egg_seed:        int
	rarity:          Rarity
	pet_name:        str
	pet_idx:         int
	secondary_stats: SecondaryStatsModel


def _build_pets_by_rarity() -> dict[str, list[dict]]:
	"""
	Build per-rarity pools in PetLibrary JSON / GameConfig registration order.
	LINQ Where+Select+ToList preserves dictionary enumeration order (no OrderBy).
	"""
	pools: dict[str, list[dict]] = {name: [] for name in RARITY_NAMES}
	for data in PET_LIBRARY.values():
		rarity_name = data["PetId"]["Rarity"]
		if rarity_name in pools:
			pools[rarity_name].append(data)
	return pools


_PETS_BY_RARITY: dict[str, list[dict]] = _build_pets_by_rarity()

_PET_STAT_COUNT: dict[str, int] = {
	k: v["NumberOfSecondStats"] for k, v in SECONDARY_STAT_PET_UNLOCK.items()
}

_UNLOCK_BY_RARITY_ORDER: list[dict] = list(SECONDARY_STAT_PET_UNLOCK.values())


def _secondary_stat_count(player: "PlayerModel | None", pet_rarity: Rarity) -> int:
	"""
	Matches PetExtensions$$CreatePet stat-count branch:
	  PetsAscensionLevel < 1  -> get_Item(chosen PetId.Rarity)
	  else                    -> Enumerable.Last(SecondaryStatPetUnlockLibrary)
	"""
	if player is not None and player.pets.ascension_model.current_level >= AscensionLevel.Mega:
		if _UNLOCK_BY_RARITY_ORDER:
			return _UNLOCK_BY_RARITY_ORDER[-1]["NumberOfSecondStats"]
		return 1
	return _PET_STAT_COUNT.get(pet_rarity.name, 1)


def predict_hatch(egg: EggModel, player: "PlayerModel | None" = None) -> HatchPrediction:
	"""
	Predict the pet type and secondary stats that will result from hatching this egg.

	Uses the seed stored in the EggModel (written at summon time, read at hatch time).
	Pass ``player`` so ascended accounts use the same stat-count rule as the game.
	"""
	rng  = RandomPCG(egg.seed)
	pool = _PETS_BY_RARITY[egg.rarity.name]
	if not pool:
		raise ValueError(f"No pets found for rarity {egg.rarity.name}")

	# PetExtensions$$CreatePet(list): RandomPCG.Choice on IList -> NextInt + indexer
	chosen = pool[rng.next_int(len(pool))]
	pet_id = chosen["PetId"]["Id"]

	# PetExtensions$$CreatePet(petId): RandomPCGExtensions.NextGuid before stats
	rng.next_guid()

	stat_count = _secondary_stat_count(player, egg.rarity)

	# SecondaryStatHelper$$GenerateSecondaryStats: Choice on IList per stat
	secondary = generate_secondary_stats(stat_count, rng)

	# Resolve display name from PetMapping
	rarity_val = egg.rarity.value
	pet_name   = next(
		(v["Name"] for v in PET_MAPPING.values()
		 if v.get("Rarity") == rarity_val and v.get("idx") == pet_id),
		f"Pet#{pet_id}",
	)

	return HatchPrediction(
		egg_seed=egg.seed,
		rarity=egg.rarity,
		pet_name=pet_name,
		pet_idx=pet_id,
		secondary_stats=secondary,
	)
