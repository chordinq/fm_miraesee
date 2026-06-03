# core/enums.py
from enum import IntEnum

class CurrencyType(IntEnum):
	Coins = 0
	Gems = 1
	Hammers = 2
	SkillSummonTickets = 3
	TechPotions = 4
	PvpTickets = 5
	ClockWinders = 6
	WarBattleTickets = 7
	Token = 8
	Eggshells = 9
	MissionEnergy = 10
	GuildPotions = 11

class TechTreeType(IntEnum):
	Forge = 0
	Power = 1
	SkillsPetTech = 2
	Clan = 3

class TechTreeNodeType(IntEnum):
	WeaponBonus = 0
	HelmetBonus = 1
	BodyBonus = 2
	ShoeBonus = 3
	GloveBonus = 4
	BeltBonus = 5
	NecklaceBonus = 6
	RingBonus = 7
	WeaponLevelUp = 8
	HelmetLevelUp = 9
	BodyLevelUp = 10
	ShoeLevelUp = 11
	GloveLevelUp = 12
	BeltLevelUp = 13
	NecklaceLevelUp = 14
	RingLevelUp = 15
	MountDamage = 16
	MountHealth = 17
	ExtraMountChance = 18
	MountSummonCost = 19
	ForgeTimerSpeed = 20
	ForgeUpgradeCost = 21
	EquipmentSellPrice = 22
	AutoForge = 23
	HammerOfflineReward = 24
	CoinOfflineReward = 25
	MaxOfflineReward = 26
	FreeForgeChance = 27
	HammerThiefHammerReward = 28
	HammerThiefCoinReward = 29
	SkillDamage = 30
	SkillPassiveDamage = 31
	SkillPassiveHealth = 32
	GhostTownSkillBonus = 33
	SkillSummonCost = 34
	PetBonusDamage = 35
	PetBonusHealth = 36
	ExtraEggChance = 37
	CommonEggTimer = 38
	RareEggTimer = 39
	EpicEggTimer = 40
	LegendaryEggTimer = 41
	UltimateEggTimer = 42
	MythicEggTimer = 43
	ZombieRushTechPotions = 44
	TechNodeUpgradeCost = 45
	TechResearchTimer = 46

class SecondaryStatType(IntEnum):
	CriticalChance = 0
	CriticalMulti = 1
	BlockChance = 2
	HealthRegen = 3
	LifeSteal = 4
	DoubleDamageChance = 5
	DamageMulti = 6
	MeleeDamageMulti = 7
	RangedDamageMulti = 8
	AttackSpeed = 9
	SkillDamageMulti = 10
	SkillCooldownMulti = 11
	HealthMulti = 12

class StatNature(IntEnum):
	Multiplier = 0
	Additive = 1
	Divisor = 2
	OneMinusMultiplier = 3

class StatType(IntEnum):
	Damage = 0
	Health = 1
	TechTreeDamage = 2
	TechTreeHealth = 3
	AscensionDamage = 4
	AscensionHealth = 5
	Experience = 6
	Cost = 7
	SellPrice = 8
	Bonus = 9
	AttackSpeed = 10

class AscendableType(IntEnum):
	Forge = 0
	Mounts = 1
	Pets = 2
	Skills = 3

class AscensionLevel(IntEnum):
	None_ = 0
	Mega = 1
	Ultra = 2
	Apex = 3

class ItemAge(IntEnum):
	Primitive = 0
	Medieval = 1
	Earlymodern = 2
	Modern = 3
	Space = 4
	Interstellar = 5
	Multiverse = 6
	Quantum = 7
	Underworld = 8
	Divine = 9

class ItemType(IntEnum):
	Helmet = 0
	Armour = 1
	Gloves = 2
	Necklace = 3
	Ring = 4
	Weapon = 5
	Shoes = 6
	Belt = 7

class Rarity(IntEnum):
	Common = 0
	Rare = 1
	Epic = 2
	Legendary = 3
	Ultimate = 4
	Mythic = 5

class CombatSkill(IntEnum):
	Meat = 0
	Morale = 1
	Arrows = 2
	Shuriken = 3
	Shout = 4
	Meteorite = 5
	Berserk = 6
	Stampede = 7
	Thorns = 8
	Bomb = 9
	Worm = 10
	Lightning = 11
	Buff = 12
	HigherMorale = 13
	RainOfArrows = 14
	StrafeRun = 15
	CannonBarrage = 16
	Drone = 17

class PetBalancingType(IntEnum):
	Balanced = 0
	Damage = 1
	Health = 2

class CombatState(IntEnum):
	Idle = 0
	WindingUp = 1
	OnCooldown = 2

class AttackType(IntEnum):
	None_ = 0
	Skill = 1
	Melee = 2
	Ranged = 3

class SummonKind(IntEnum):
	Skills = 0
	Pets = 1
	Mounts = 2

class DungeonType(IntEnum):
	Hammer = 0
	Skill = 1
	Pet = 2
	Potion = 3
