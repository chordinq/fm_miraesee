# configs/display.py
"""
Display-name overrides for enum members used in formatted output.
Keys match SecondaryStatType member names exactly.
"""

STAT_DISPLAY_NAMES: dict[str, str] = {
	"CriticalChance":      "Critical Chance",
	"CriticalMulti":       "Critical Damage",
	"BlockChance":         "Block Chance",
	"HealthRegen":         "Health Regen",
	"LifeSteal":           "Life Steal",
	"DoubleDamageChance":  "Double Chance",
	"DamageMulti":         "Damage",
	"MeleeDamageMulti":    "Melee Damage",
	"RangedDamageMulti":   "Ranged Damage",
	"AttackSpeed":         "Attack Speed",
	"SkillDamageMulti":    "Skill Damage",
	"SkillCooldownMulti":  "Skill Cooldown",
	"HealthMulti":         "Health",
}
