# tests/run_summon_from_dump.py
"""Quick summon test: skill x5, egg x1, mount x1 from dump state."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from configs import SKILL_LIBRARY, MOUNT_MAPPING
from core.game_logic.GameLogic import GameLogic
from utils.parser import parse_dump

DUMP = """
[CURRENCY]
00A9000E00000DCE000110BB00002B4C
000017B70000000500000C6500000000
0000007000001788000000000000007D

[TECH_TREE]
00040014002400410031005000640074
0084009400B400A400C400D000E000F0
01040114012201320140015001601011
10311051107110021021104110611080
109010A310C310B310D310F310E31103
11131124113411401150116011701180
119011A011B011C011D011E011F01200
12101220123012401250126212722004
20102020203020442053206420742080
209120A020B020C020D020E420F42104
21142120213021402154216021702183
219021A021B021C021D021E021F42200
221022202230224022502264F000F000

[FORGE]
00169665DD1A85C60CBF000000000000

[SKILL]
164F9665DD1A85C33426000000000000

[PET]
1C0F9665DD1A85C33083000000000000

[MOUNT]
0D029665DD1A85C33045000000000000

[SKILL_COLLECTION]
1020260400FF00000000000000000000
1000240100FF00000000000000000000
1040270200FF00000000000000000000
1030250300FF00000000000000000000
1060260100FF00000000000000000000
1100260400FF00000000000000000000
10C00801010100000000000000000000
1080070100FF00000000000000000000
10E00702010200000000000000000000
10900001010000000000000000000000
"""

# --- name helpers -----------------------------------------------------------

def skill_name(detail: str) -> str:
    """detail is SKILL_LIBRARY key (no spaces); recover proper name."""
    # SKILL_LIBRARY keys are already the canonical names
    for key in SKILL_LIBRARY:
        if key.replace(" ", "") == detail:
            return key
    return detail

def pet_name(rarity_val: int, pet_id: int) -> str:
    key = f"{rarity_val}_{pet_id}"
    return PET_MAPPING.get(key, {}).get("Name", f"PetId{pet_id}")

def mount_name(detail: str) -> str:
    # mount_summon_sim already stores the name (spaces stripped)
    # recover from MountMapping
    for data in MOUNT_MAPPING.values():
        if data["Name"].replace(" ", "") == detail:
            return data["Name"]
    return detail

# ---------------------------------------------------------------------------

def main():
    player = parse_dump(DUMP)
    gl     = GameLogic(player)
    sm_skill = player.skills.summon_model
    sm_egg   = player.pets.summon_model
    sm_mount = player.mounts.summon_model

    print("=== SKILL SUMMON (x5) ===")
    print(f"  seed={sm_skill.get_seed():#018x}  level={sm_skill.level}  count={sm_skill.count}")
    result = gl.summon_skills(5)
    if not result.success:
        print(f"  FAILED: {result.error}")
    else:
        for i, p in enumerate(result.pulls, 1):
            bonus = " (BONUS)" if p.is_bonus else ""
            new   = " [NEW]"  if p.is_new  else ""
            print(f"  #{i}  {p.rarity.name:10}  {skill_name(p.detail)}{new}{bonus}")
    print(f"  -> seed={sm_skill.get_seed():#018x}  level={sm_skill.level}  count={sm_skill.count}")

    print()
    print("=== EGG SUMMON (x1) ===")
    print(f"  seed={sm_egg.get_seed():#018x}  level={sm_egg.level}  count={sm_egg.count}")
    result = gl.summon_eggs(1)
    if not result.success:
        print(f"  FAILED: {result.error}")
    else:
        for i, p in enumerate(result.pulls, 1):
            bonus = " (BONUS)" if p.is_bonus else ""
            print(f"  #{i}  {p.rarity.name:10}  {p.detail}{bonus}")
    print(f"  -> seed={sm_egg.get_seed():#018x}  level={sm_egg.level}  count={sm_egg.count}")

    print()
    print("=== MOUNT SUMMON (x1) ===")
    print(f"  seed={sm_mount.get_seed():#018x}  level={sm_mount.level}  count={sm_mount.count}")
    result = gl.summon_mounts(1)
    if not result.success:
        print(f"  FAILED: {result.error}")
    else:
        for i, p in enumerate(result.pulls, 1):
            bonus = " (BONUS)" if p.is_bonus else ""
            new   = " [NEW]"  if p.is_new  else ""
            stats_str = ""
            if p.secondary_stats:
                parts = []
                for s in p.secondary_stats.stats:
                    parts.append(f"{s.stat_type.name}({s.perfection*100:.2f}%)")
                stats_str = "  stats=[" + ", ".join(parts) + "]"
            print(f"  #{i}  {p.rarity.name:10}  {mount_name(p.detail)}{new}{bonus}{stats_str}")
    print(f"  -> seed={sm_mount.get_seed():#018x}  level={sm_mount.level}  count={sm_mount.count}")


if __name__ == "__main__":
    main()
