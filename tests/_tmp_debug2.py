"""
Pet = next_int(N) for type. Now debug stat generation.
Trying different excluded type sets and extra-PCG-call counts.

Correct answers:
  Slot 0 (Hedgehog,  seed 0x9665DD1A85C33041) -> HealthRegen    perf ~35.75%  (1.43/4)
  Slot 1 (Ostrich,   seed 0x9665DD1A85C33042) -> AttackSpeed    perf ~92.0%   (36.8/40)
  Slot 2 (Bear,      seed 0x9665DD1A85C33045) -> SkillCooldown  perf ~?
  Slot 3 (Scorpion,  seed 0x9665DD1A85C33046) -> CriticalChance perf ~40.4%   (4.04/10)
"""
import sys
sys.path.insert(0, '.')
from core.random_pcg import RandomPCG
from core.enums import SecondaryStatType
from core.game_logic.player_model.SecondaryStatsModel import SecondaryStatsModel
from core.game_logic.player_model.StatModel import StatModel
from configs import PET_LIBRARY, SECONDARY_STAT_PET_UNLOCK

RARE_POOL = sorted(
    [v for v in PET_LIBRARY.values() if v["PetId"]["Rarity"] == "Rare"],
    key=lambda v: v["PetId"]["Id"],
)
N = len(RARE_POOL)
STAT_COUNT = SECONDARY_STAT_PET_UNLOCK.get("Rare", {}).get("NumberOfSecondStats", 1)

SEEDS = [
    (0, 0x9665DD1A85C33041, "Hedgehog",  "HealthRegen",        35.75),
    (1, 0x9665DD1A85C33042, "Ostrich",   "AttackSpeed",        92.0),
    (2, 0x9665DD1A85C33045, "Bear",      "SkillCooldownMulti", None),
    (3, 0x9665DD1A85C33046, "Scorpion",  "CriticalChance",     40.4),
]

ALL_TYPES  = list(SecondaryStatType)
# Exclude weapon-specific stats
EXCL_MELEE_RANGED = [SecondaryStatType.MeleeDamageMulti, SecondaryStatType.RangedDamageMulti]
PET_TYPES  = [t for t in ALL_TYPES if t not in EXCL_MELEE_RANGED]

def gen_stats(stat_count, rng, avail):
    result = []
    pool = list(avail)
    for _ in range(stat_count):
        if not pool: break
        t = rng.choice(pool)
        p = rng.next_f64()
        result.append((t, p))
        pool.remove(t)
    return result

def try_variant(label, extra_pcg_calls, stat_pool):
    print(f"\n=== {label} ===")
    all_ok = True
    for slot, seed, exp_name_pet, exp_stat, exp_perf in SEEDS:
        rng = RandomPCG(seed)
        idx = rng.next_int(N)
        for _ in range(extra_pcg_calls):
            rng._next_pcg32()
        stats = gen_stats(STAT_COUNT, rng, stat_pool)
        stype = stats[0][0].name if stats else "-"
        sperf = stats[0][1] * 100 if stats else 0
        ok_stat = stype == exp_stat
        ok_perf = exp_perf is None or abs(sperf - exp_perf) < 2.0
        status = "OK" if (ok_stat and ok_perf) else ("TYPE_WRONG" if not ok_stat else "PERF_WRONG")
        if not (ok_stat and ok_perf): all_ok = False
        print(f"  Slot {slot}: {stype:22} ({sperf:.1f}%)  [{status}]  (expected {exp_stat} {f'~{exp_perf:.1f}%' if exp_perf else ''})")
    if all_ok: print("  *** ALL CORRECT ***")

# Variant C baseline: 0 extra calls, all 13 types
try_variant("C: 0 extra, all 13 types", 0, ALL_TYPES)

# Variant E: 0 extra, 11 pet types (excl melee/ranged)
try_variant("E: 0 extra, 11 pet types", 0, PET_TYPES)

# Variant F: 1 extra, 11 pet types
try_variant("F: 1 extra, 11 pet types", 1, PET_TYPES)

# Variant G: 2 extra, 11 pet types
try_variant("G: 2 extra, 11 pet types", 2, PET_TYPES)

# Variant H: 4 extra (guid), 11 pet types
try_variant("H: 4 extra (guid), 11 pet types", 4, PET_TYPES)

# Variant I: 1 extra, all 13
try_variant("I: 1 extra, all 13", 1, ALL_TYPES)

# Variant J: 2 extra, all 13
try_variant("J: 2 extra, all 13", 2, ALL_TYPES)
