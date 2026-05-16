# constants.py

COLOR_RESET = "\033[0m"

RARITY_KOR = {
    "Common": "일반",
    "Rare": "희귀",
    "Epic": "서사",
    "Legendary": "전설",
    "Ultimate": "궁극",
    "Mythic": "신화"
}

RARITY_COLOR = {
    "Common": "\033[38;2;241;241;241m",
    "Rare": "\033[38;2;93;216;255m",
    "Epic": "\033[38;2;93;255;138m",
    "Legendary": "\033[38;2;252;255;93m",
    "Ultimate": "\033[38;2;255;93;93m",
    "Mythic": "\033[38;2;213;93;255m"
}

TYPE_COLOR = {
    "Health": "\033[38;2;46;204;113m",
    "Damage": "\033[38;2;255;87;34m",
    "Balanced": "\033[38;2;52;152;219m"
}

# 밸런스 패치 반영 (Double Chance: 40% -> 20% / Critical Damage: 100% -> 80%)
SUBSTATS_INFO = {
    "Critical Chance": (0.01, 0.12),
    "Critical Damage": (0.01, 0.80),
    "Block Chance": (0.01, 0.05),
    "Health Regen": (0.01, 0.04),
    "Life Steal": (0.01, 0.20),
    "Double Chance": (0.01, 0.20),
    "Damage": (0.01, 0.15),
    "Melee Damage": (0.01, 0.50),
    "Ranged Damage": (0.01, 0.15),
    "Attack Speed": (0.01, 0.40),
    "Skill Damage": (0.01, 0.30),
    "Skill Cooldown": (0.01, 0.07),
    "Health": (0.01, 0.15)
}
SUBSTATS_POOL = list(SUBSTATS_INFO.keys())

RARITY_SCORE = {
    "Mythic": 6, "Ultimate": 5, "Legendary": 4, 
    "Epic": 3, "Rare": 2, "Common": 1
}

def get_gradient_color(perf_pct):
    perf = max(0.0, min(100.0, perf_pct))
    if perf < 50:
        r = 255
        g = int(255 * (perf / 50.0))
    else:
        r = int(255 * ((100.0 - perf) / 50.0))
        g = 255
    b = 0
    return f"\033[38;2;{r};{g};{b}m"

def get_substat_value(stat_name, pcg_f64_val):
    low, up = SUBSTATS_INFO[stat_name]
    return low + pcg_f64_val * (up - low)