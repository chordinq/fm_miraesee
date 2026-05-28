# configs/enum_en_lookup.py — IntEnum member → string_tables English key
from __future__ import annotations

from core.enums import RARITY_NAMES, CombatSkill, CurrencyType, ItemAge, ItemType, Rarity

# (EnumClassName, member_name) → exact "en" in string_tables_en_ko_ja.json
ENUM_MEMBER_EN_OVERRIDES: dict[tuple[str, str], str] = {
    ("ItemAge", "Earlymodern"): "Early-Modern",
    ("CombatSkill", "RainOfArrows"): "Arrow Rain",
    ("CombatSkill", "Shuriken"): "Shurikens",
    ("CurrencyType", "SkillSummonTickets"): "Skill Summon Tickets",
    ("CurrencyType", "TechPotions"): "Tech Potions",
    ("CurrencyType", "PvpTickets"): "PvP Tickets",
    ("CurrencyType", "ClockWinders"): "Clock Winders",
    ("CurrencyType", "WarBattleTickets"): "War Battle Tickets",
    ("CurrencyType", "Eggshells"): "Eggshells",
    ("CurrencyType", "MissionEnergy"): "Mission Energy",
    ("CurrencyType", "GuildPotions"): "Guild Potions",
    ("TechTreeType", "SkillsPetTech"): "Skills & Pet Tech",
    ("TechTreeNodeType", "WeaponBonus"): "Weapon Bonus",
    ("TechTreeNodeType", "HelmetBonus"): "Helmet Bonus",
    ("TechTreeNodeType", "BodyBonus"): "Body Bonus",
    ("TechTreeNodeType", "ShoeBonus"): "Shoe Bonus",
    ("TechTreeNodeType", "GloveBonus"): "Glove Bonus",
    ("TechTreeNodeType", "BeltBonus"): "Belt Bonus",
    ("TechTreeNodeType", "NecklaceBonus"): "Necklace Bonus",
    ("TechTreeNodeType", "RingBonus"): "Ring Bonus",
    ("TechTreeNodeType", "WeaponLevelUp"): "Weapon Level Up",
    ("TechTreeNodeType", "HelmetLevelUp"): "Helmet Level Up",
    ("TechTreeNodeType", "BodyLevelUp"): "Body Level Up",
    ("TechTreeNodeType", "ShoeLevelUp"): "Shoe Level Up",
    ("TechTreeNodeType", "GloveLevelUp"): "Glove Level Up",
    ("TechTreeNodeType", "BeltLevelUp"): "Belt Level Up",
    ("TechTreeNodeType", "NecklaceLevelUp"): "Necklace Level Up",
    ("TechTreeNodeType", "RingLevelUp"): "Ring Level Up",
    ("SecondaryStatType", "CriticalMulti"): "Critical Multi",
    ("SecondaryStatType", "BlockChance"): "Block Chance",
    ("SecondaryStatType", "HealthRegen"): "Health Regen",
    ("SecondaryStatType", "LifeSteal"): "Life Steal",
    ("SecondaryStatType", "DoubleDamageChance"): "Double Damage Chance",
    ("SecondaryStatType", "DamageMulti"): "Damage Multi",
    ("SecondaryStatType", "MeleeDamageMulti"): "Melee Damage Multi",
    ("SecondaryStatType", "RangedDamageMulti"): "Ranged Damage Multi",
    ("SecondaryStatType", "AttackSpeed"): "Attack Speed",
    ("SecondaryStatType", "SkillDamageMulti"): "Skill Damage Multi",
    ("SecondaryStatType", "SkillCooldownMulti"): "Skill Cooldown Multi",
    ("SecondaryStatType", "HealthMulti"): "Health Multi",
    ("AscensionLevel", "None_"): "None",
    ("AttackType", "None_"): "None",
}


def _split_camel(name: str) -> str:
    parts: list[str] = []
    buf = ""
    for ch in name:
        if ch.isupper() and buf:
            parts.append(buf)
            buf = ch
        else:
            buf += ch
    if buf:
        parts.append(buf)
    return " ".join(parts)


def member_en_key(enum_cls_name: str, member_name: str) -> str:
    override = ENUM_MEMBER_EN_OVERRIDES.get((enum_cls_name, member_name))
    if override:
        return override
    if member_name == "None_":
        return "None"
    return _split_camel(member_name)


def item_age_en_keys() -> dict[int, str]:
    return {int(m.value): member_en_key("ItemAge", m.name) for m in ItemAge}


def item_type_en_keys() -> dict[int, str]:
    return {int(m.value): member_en_key("ItemType", m.name) for m in ItemType}


def rarity_en_keys() -> dict[int, str]:
    return {i: RARITY_NAMES[i] for i in range(len(RARITY_NAMES))}


def currency_en_keys() -> dict[int, str]:
    return {int(m.value): member_en_key("CurrencyType", m.name) for m in CurrencyType}


def combat_skill_en_keys_from_mapping() -> dict[int, str]:
    from configs.config import SKILL_MAPPING

    by_enum: dict[int, str] = {}
    for entry in SKILL_MAPPING.values():
        by_enum[int(entry["Enum"])] = str(entry["Name"])
    for m in CombatSkill:
        by_enum.setdefault(int(m.value), member_en_key("CombatSkill", m.name))
    return by_enum
