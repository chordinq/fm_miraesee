# core/game_logic/pet_egg_hatch.py
"""
Pet egg hatch prediction.

C# PetEggHatchFinalizedAction$$Execute flow:
  1. Filter PetConfig (PetLibrary) entries where PetId.Rarity == egg.rarity
  2. Select PetId keys -> ToList  (sorted by PetId.Id via GameConfig ordering)
  3. rng = RandomPCG.CreateFromSeed(egg.seed)
  4. pet = PetExtensions.CreatePet(player, pet_id_list, rng)
        -> rng.NextInt(count)                : select pet type  (1 PCG call)
        -> rng.NextGuid()                    : pet unique ID     (4 PCG calls)
        -> generate_secondary_stats(n, rng)  : secondary stats
             -> rng.NextInt(available)       : stat type        (1 PCG call each)
             -> rng.NextF64()               : perfection        (1 PCG call each)

Pet type/stat prediction is fully deterministic from the stored egg seed.
"""

from __future__ import annotations

from dataclasses import dataclass

from configs import PET_LIBRARY, PET_MAPPING, SECONDARY_STAT_PET_UNLOCK
from core.enums import Rarity, RARITY_NAMES
from core.random_pcg import RandomPCG
from core.game_logic.player_model.EggModel import EggModel
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.secondary_stats import generate_secondary_stats


@dataclass
class HatchPrediction:
	egg_seed:        int
	rarity:          Rarity
	pet_name:        str
	pet_idx:         int
	secondary_stats: SecondaryStatsModel


def _build_pets_by_rarity() -> dict[str, list[dict]]:
	"""
	Build pools of pet library entries grouped by rarity, sorted by PetId.Id.
	Mirrors C# GameConfig<PetId, PetConfig> iteration order.
	"""
	pools: dict[str, list[dict]] = {name: [] for name in RARITY_NAMES}
	for data in sorted(PET_LIBRARY.values(), key=lambda v: v["PetId"]["Id"]):
		rarity_name = data["PetId"]["Rarity"]
		if rarity_name in pools:
			pools[rarity_name].append(data)
	return pools


_PETS_BY_RARITY: dict[str, list[dict]] = _build_pets_by_rarity()

_PET_STAT_COUNT: dict[str, int] = {
	k: v["NumberOfSecondStats"] for k, v in SECONDARY_STAT_PET_UNLOCK.items()
}


def predict_hatch(egg: EggModel) -> HatchPrediction:
	"""
	Predict the pet type and secondary stats that will result from hatching this egg.

	Uses the seed stored in the EggModel (written at summon time, read at hatch time).
	"""
	rng  = RandomPCG(egg.seed)
	pool = _PETS_BY_RARITY[egg.rarity.name]
	if not pool:
		raise ValueError(f"No pets found for rarity {egg.rarity.name}")

	# PetExtensions$$CreatePet overload 1: rng.Choice(petIdList)
	# C# uses list[NextInt(count)] -- 1 PCG call
	chosen = pool[rng.next_int(len(pool))]
	pet_id = chosen["PetId"]["Id"]

	# PlayerPetModel constructor generates a MetaplayUUID via rng.NextGuid() -- 4 PCG calls
	rng.next_guid()

	stat_count = _PET_STAT_COUNT.get(egg.rarity.name, 1)

	# SecondaryStatHelper$$GenerateSecondaryStats (uses next_int(N) for type, next_f64 for perfection)
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
