"""
Decode actual pet stats from the dump to understand the stat type mapping.
Line: 22041861010014F01487010000000000
       kind=2, rarity=2(Epic), id=04, prog=28chars
"""
import sys
sys.path.insert(0, '.')
from core.enums import SecondaryStatType

# Decode stats from the 3 Epic pets already owned
# prog (28 chars) = {level:02X}{exp:02X}{is_eq:02X}{slot:02X} + stats(20 chars)
PETS = [
    ("Panda eq slot0",    "22041861010014F01487010000000000"),
    ("SaberTooth eq",     "2201175D010119D51203850000000000"),
    ("Panda slot2",       "220418F1010216F73720900000000000"),
]

print("=== Decoding owned Epic pets ===")
for name, line in PETS:
    # header: kind(1) + rarity(1) + id(2) = 4 chars
    # prog: 28 chars = level(2)+exp(2)+eq(2)+slot(2) + stats(20)
    prog = line[4:]                     # 28 chars
    level       = int(prog[0:2], 16)
    exp         = int(prog[2:4], 16)
    is_eq       = int(prog[4:6], 16)
    slot        = int(prog[6:8], 16)
    stats_str   = prog[8:28]            # 20 chars = stat1(10) + stat2(10)

    def decode_stat(s10):
        if s10 == "0000000000":
            return None
        kind   = int(s10[1], 16)        # type nibble
        perf32 = int(s10[2:10], 16)     # lower 32 bits
        perf   = perf32 / 4294967296.0
        try:
            stype = SecondaryStatType(kind)
        except ValueError:
            stype = f"type{kind}"
        return stype, perf

    s1 = decode_stat(stats_str[0:10])
    s2 = decode_stat(stats_str[10:20])
    print(f"\n  {name}: level={level} exp={exp} eq={is_eq} slot={slot}")
    if s1: print(f"    Stat1: {s1[0].name if hasattr(s1[0],'name') else s1[0]} ({s1[1]*100:.2f}%)")
    if s2: print(f"    Stat2: {s2[0].name if hasattr(s2[0],'name') else s2[0]} ({s2[1]*100:.2f}%)")

print()
print("=== SecondaryStatType enum values ===")
for s in SecondaryStatType:
    print(f"  {s.value}: {s.name}")
