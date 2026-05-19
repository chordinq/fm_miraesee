import unicodedata

def get_display_width(s):
    return sum(2 if unicodedata.east_asian_width(c) in 'WFA' else 1 for c in str(s))

def get_padded_kor(text, width):
    text = str(text)
    dw = get_display_width(text)
    if dw >= width: return text
    pad_total = width - dw
    pad_left = pad_total // 2
    pad_right = pad_total - pad_left
    return " " * pad_left + text + " " * pad_right

def parse_kwargs(args):
    kwargs = {}
    pos_args = []
    for a in args:
        if ':' in a:
            k, v = a.split(':', 1)
            kwargs[k.lower()] = v
        else:
            pos_args.append(a)
    return kwargs, pos_args

COLOR_RESET = "\033[0m"

# 모듈별 테마 색상 (프롬프트 및 제목용)
UI_COLORS = {
    "Forge": "\033[97m",   # Bright White
    "Skill": "\033[92m",   # Bright Green
    "Pet": "\033[94m",     # Bright Blue
    "Mount": "\033[93m",   # Bright Yellow
    "Global": "\033[90m"   # Gray
}

RARITY_KOR = {
    "Common": "일반", "Rare": "희귀", "Epic": "서사",
    "Legendary": "전설", "Ultimate": "궁극", "Mythic": "신화"
}

RARITY_COLOR = {
    "Common": "\033[38;2;241;241;241m", "Rare": "\033[38;2;93;216;255m",
    "Epic": "\033[38;2;93;255;138m", "Legendary": "\033[38;2;252;255;93m",
    "Ultimate": "\033[38;2;255;93;93m", "Mythic": "\033[38;2;213;93;255m"
}

AGE_NAME = {
    0: "Primitive", 1: "Medieval", 2: "Early-Modern", 3: "Modern", 4: "Space",
    5: "Interstellar", 6: "Multiverse", 7: "Quantum", 8: "Underworld", 9: "Divine"
}

AGE_COLOR = {
    0: "\033[38;2;241;241;241m", 1: "\033[38;2;93;216;255m", 2: "\033[38;2;93;255;138m",
    3: "\033[38;2;252;255;93m", 4: "\033[38;2;255;93;93m", 5: "\033[38;2;213;93;255m",
    6: "\033[38;2;117;255;238m", 7: "\033[38;2;125;93;255m", 8: "\033[38;2;176;120;121m",
    9: "\033[38;2;255;158;13m"
}

AGE_KOR_SPACED = {
    0: "원시", 1: "중세", 2: "근대초기", 3: "현대", 4: "우주",
    5: "항성", 6: "다중우주", 7: "양자", 8: "지하세계", 9: "신성"
}

TYPE_KOR_SPACED = {
    "Melee Weapon": "근거리", "Ranged Weapon": "원거리",
    "Helmet": "투구", "Armour": "갑옷", "Gloves": "장갑",
    "Shoes": "신발", "Belt": "벨트", "Necklace": "목걸이", "Ring": "반지"
}

TYPE_COLOR = {
    "Health": "\033[38;2;46;204;113m", "Damage": "\033[38;2;255;87;34m", "Balanced": "\033[38;2;52;152;219m"
}

SUBSTATS_INFO = {
    "Critical Chance": (0.01, 0.12), "Critical Damage": (0.01, 0.80),
    "Block Chance": (0.01, 0.05), "Health Regen": (0.01, 0.04),
    "Life Steal": (0.01, 0.20), "Double Chance": (0.01, 0.20),
    "Damage": (0.01, 0.15), "Melee Damage": (0.01, 0.50),
    "Ranged Damage": (0.01, 0.15), "Attack Speed": (0.01, 0.40),
    "Skill Damage": (0.01, 0.30), "Skill Cooldown": (0.01, 0.07),
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