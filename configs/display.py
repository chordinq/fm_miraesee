# configs/display.py
"""
Display-name overrides for enum members used in formatted output.
Keys match SecondaryStatType member names exactly.
"""

STAT_DISPLAY_NAMES: dict[str, str] = {
	"SkillCooldownMulti":  "Skill Cooldown",
	"CriticalMulti":       "Critical Damage",
	"DoubleDamageChance":  "Double Chance",
	"MeleeDamageMulti":    "Melee Damage",
	"RangedDamageMulti":   "Ranged Damage",
	"HealthMulti":         "Health",
	"DamageMulti":         "Damage",
	"SkillDamageMulti":    "Skill Damage",
	"HealthRegen":         "Health Regen",
}
