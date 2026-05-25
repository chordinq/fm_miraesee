"""
Debug hatch prediction by trying different RNG flows and pool orderings.
Known correct answers:
  Slot 0 seed 0x9665DD1A85C33041 -> Hedgehog  + HealthRegen  1.43% (max 4%)
  Slot 1 seed 0x9665DD1A85C33042 -> Ostrich   + AttackSpeed  36.8% (max 40%)
  Slot 2 seed 0x9665DD1A85C33045 -> Bear      + SkillCooldown
  Slot 3 seed 0x9665DD1A85C33046 -> Scorpion  + CriticalChance 4.04%
"""
import sys, json
sys.path.insert(0, '.')

from core.random_pcg import RandomPCG
from core.game_logic.secondary_stats import generate_secondary_stats
from configs import PET_LIBRARY, PET_MAPPING, SECONDARY_STAT_PET_UNLOCK

# Build pool: Rare pets sorted by Id (game config order matches Id order)
RARE_POOL = sorted(
    [v for v in PET_LIBRARY.values() if v["PetId"]["Rarity"] == "Rare"],
    key=lambda v: v["PetId"]["Id"],
)
N = len(RARE_POOL)

def pet_name(pet_id):
    for v in PET_MAPPING.values():
        if v["Rarity"] == 1 and v["idx"] == pet_id:
            return v["Name"]
    return f"PetId#{pet_id}"

STAT_COUNT = SECONDARY_STAT_PET_UNLOCK.get("Rare", {}).get("NumberOfSecondStats", 1)

SEEDS = [
    (0, 0x9665DD1A85C33041, "Hedgehog",  "HealthRegen",         1.43 / 4.0),
    (1, 0x9665DD1A85C33042, "Ostrich",   "AttackSpeed",         36.8 / 40.0),
    (2, 0x9665DD1A85C33045, "Bear",      "SkillCooldownMulti",  None),
    (3, 0x9665DD1A85C33046, "Scorpion",  "CriticalChance",      4.04 / 10.0),
]

def test(label, get_pet_idx, with_guid):
    print(f"\n=== {label} ===")
    for slot, seed, exp_name, exp_stat, exp_perf in SEEDS:
        rng = RandomPCG(seed)
        idx = get_pet_idx(rng, N)
        pet_id = RARE_POOL[idx]["PetId"]["Id"]
        if with_guid:
            rng.next_guid()
        sec = generate_secondary_stats(STAT_COUNT, rng)
        name = pet_name(pet_id)
        s0 = sec.stats[0] if sec.stats else None
        stat_name = s0.stat_type.name if s0 else "-"
        perf_pct  = s0.perfection * 100 if s0 else 0
        ok_name = "OK" if name == exp_name else f"WRONG(expected {exp_name})"
        ok_stat = "OK" if exp_stat and stat_name == exp_stat else f"WRONG(expected {exp_stat})"
        print(f"  Slot {slot}: {name:12} {ok_name:30}  {stat_name}({perf_pct:.1f}%)  {ok_stat}")

# Variant A: reservoir sampling (choice), no guid
test("A: choice, no guid",
     lambda rng, n: RARE_POOL.index(rng.choice(RARE_POOL)),
     with_guid=False)

# Variant B: reservoir sampling (choice), with guid
test("B: choice, with guid",
     lambda rng, n: RARE_POOL.index(rng.choice(RARE_POOL)),
     with_guid=True)

# Variant C: direct next_int(N), no guid
test("C: next_int(N), no guid",
     lambda rng, n: rng.next_int(n),
     with_guid=False)

# Variant D: direct next_int(N), with guid
test("D: next_int(N), with guid",
     lambda rng, n: rng.next_int(n),
     with_guid=True)
