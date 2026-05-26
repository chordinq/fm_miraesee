# constants/colors.py
def _hex_fg(hex_color: str) -> str:
	r = int(hex_color[1:3], 16)
	g = int(hex_color[3:5], 16)
	b = int(hex_color[5:7], 16)
	return f"\033[38;2;{r};{g};{b}m"

def _hex_bg(hex_color: str) -> str:
	r = int(hex_color[1:3], 16)
	g = int(hex_color[3:5], 16)
	b = int(hex_color[5:7], 16)
	return f"\033[48;2;{r};{g};{b}m"

BG_HEX        = "#101214"
BG_PANEL_HEX  = "#1a1e24"   # slightly brighter — tables / resource bar
FG_HEX        = "#FFFFFF"
BG_DEFAULT    = _hex_bg(BG_HEX)
BG_PANEL      = _hex_bg(BG_PANEL_HEX)
TXT_DEFAULT   = _hex_fg(FG_HEX)
LINE_DEFAULT = _hex_fg("#D0D0D0")

# Default reset; terminal bg from OSC (screen.set_terminal_theme).
RESET       = "\033[0m"
RESET_PANEL = f"\033[39m{BG_PANEL}"   # after colored text inside a panel line

SYS_INFO    = _hex_fg("#3498db")
SYS_SUCCESS = _hex_fg("#07bc0c")
SYS_WARNING = _hex_fg("#f1c40f")
SYS_ERROR   = _hex_fg("#e74c3c")

COLOR_PRIMITIVE     = _hex_fg("#F1F1F1")
COLOR_MEDIEVAL      = _hex_fg("#5DD8FF")
COLOR_EARLY_MODERN  = _hex_fg("#5DFF8A")
COLOR_MODERN        = _hex_fg("#FCFF5D")
COLOR_SPACE         = _hex_fg("#FF5D5D")
COLOR_INTERSTELLAR  = _hex_fg("#D55DFF")
COLOR_MULTIVERSE    = _hex_fg("#75FFEE")
COLOR_QUANTUM       = _hex_fg("#7D5DFF")
COLOR_UNDERWORLD    = _hex_fg("#B07879")
COLOR_DIVINE        = _hex_fg("#FF9E0D")

COLOR_GEMS              = _hex_fg("#db6d94")
COLOR_COINS             = _hex_fg("#edc15d")
COLOR_HAMMERS           = _hex_fg("#96431a")
COLOR_EGGSHELLS         = _hex_fg("#c9c9c9")
COLOR_CLOCK_WINDERS     = _hex_fg("#e7a055")
COLOR_TECH_POTIONS      = _hex_fg("#a62318")
COLOR_SKILL_TICKETS     = _hex_fg("#8bfa4e")

AGE_COLORS = {
	0: COLOR_PRIMITIVE,
	1: COLOR_MEDIEVAL,
	2: COLOR_EARLY_MODERN,
	3: COLOR_MODERN,
	4: COLOR_SPACE,
	5: COLOR_INTERSTELLAR,
	6: COLOR_MULTIVERSE,
	7: COLOR_QUANTUM,
	8: COLOR_UNDERWORLD,
	9: COLOR_DIVINE
}

RARITY_COLORS = {
	0: COLOR_PRIMITIVE,     # Common
	1: COLOR_MEDIEVAL,      # Rare
	2: COLOR_EARLY_MODERN,  # Epic
	3: COLOR_MODERN,        # Legendary
	4: COLOR_SPACE,         # Ultimate
	5: COLOR_INTERSTELLAR   # Mythic
}

CURRENCY_COLORS: dict[str, str] = {
	"Gems":               COLOR_GEMS,
	"Coins":              COLOR_COINS,
	"Hammers":            COLOR_HAMMERS,
	"Eggshells":          COLOR_EGGSHELLS,
	"ClockWinders":       COLOR_CLOCK_WINDERS,
	"TechPotions":        COLOR_TECH_POTIONS,
	"SkillSummonTickets": COLOR_SKILL_TICKETS,
}