from enum import IntEnum
from ..miraesee_extension import miraesee_extension

class AscensionLevel(IntEnum):
	None_ = 0
	Mega = 1
	Ultra = 2
	Apex = 3

class AscendableType(IntEnum):
	Forge = 0
	Mounts = 1
	Pets = 2
	Skills = 3

class BattleMode(IntEnum):
	None_ = 0
	MainBattle = 1
	DungeonBattle = 2
	PvpBattle = 3
	GuildWarBattle = 4
	MissionReplay = 5

class BattleState(IntEnum):
	None_ = 0
	ReadyToStartWave = 1
	WaveFinished = 2
	Running = 3
	Paused = 4
	Won = 5
	Lost = 6

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

class CombatState(IntEnum):
	Idle = 0
	WindingUp = 1
	OnCooldown = 2

class AttackType(IntEnum):
	None_ = 0
	Skill = 1
	Melee = 2
	Ranged = 3

class DungeonType(IntEnum):
	Hammer = 0
	Skill = 1
	Pet = 2
	Potion = 3
	
class ColorType(IntEnum):
	Background = 0
	Foreground = 1

class GuildTier(IntEnum):
	SSS = -2
	SS = -1
	S = 0
	A = 1
	B = 2
	C = 3
	D = 4
	E = 5
	F = 6

class GuildCreationFailedEnum(IntEnum):
	None_ = 0
	NameNotUnique = 1
	TagNotUnique = 2
	BadWord = 3
	NameEmpty = 4
	NameTooLong = 5
	TagEmpty = 6
	TagTooLong = 7
	NameRegexFailed = 8
	TagRegexFailed = 9
	Other = 10

class MissionState(IntEnum):
	None_ = 0
	Rally = 1
	Finalizing = 2
	Finished = 3

class WarTask(IntEnum):
	SpendCoinsOnForge = 100
	StartForgeUpgrade = 101
	CompleteForgeUpgrade = 102
	SpendGemOnForge = 103
	ForgePrimitiveEquipment = 1000
	ForgeMedievalEquipment = 1001
	ForgeEarlyModernEquipment = 1002
	ForgeModernEquipment = 1003
	ForgeSpaceEquipment = 1004
	ForgeInterstellarEquipment = 1005
	ForgeMultiverseEquipment = 1006
	ForgeQuantumEquipment = 1007
	ForgeUnderworldEquipment = 1008
	ForgeDivineEquipment = 1009
	UseHammerThiefDungeonKey = 2000
	UseGhostTownDungeonKey = 2001
	UseInvasionDungeonKey = 2002
	UseZombieInvasionDungeonKey = 2003
	SummonCommonSkill = 3000
	SummonRareSkill = 3001
	SummonEpicSkill = 3002
	SummonLegendarySkill = 3003
	SummonUltimateSkill = 3004
	SummonMythicSkill = 3005
	UpgradeCommonSkill = 4006
	UpgradeRareSkill = 4007
	UpgradeEpicSkill = 4008
	UpgradeLegendarySkill = 4009
	UpgradeUltimateSkill = 4010
	UpgradeMythicSkill = 4011
	HatchCommonEgg = 5000
	HatchRareEgg = 5001
	HatchEpicEgg = 5002
	HatchLegendaryEgg = 5003
	HatchUltimateEgg = 5004
	HatchMythicEgg = 5005
	SummonCommonEgg = 5010
	SummonRareEgg = 5011
	SummonEpicEgg = 5012
	SummonLegendaryEgg = 5013
	SummonUltimateEgg = 5014
	SummonMythicEgg = 5015
	MergeCommonPet = 6000
	MergeRarePet = 6001
	MergeEpicPet = 6002
	MergeLegendaryPet = 6003
	MergeUltimatePet = 6004
	MergeMythicPet = 6005
	FinishITechTreeUpgrade = 7000
	FinishIITechTreeUpgrade = 7001
	FinishIIITechTreeUpgrade = 7002
	FinishIVTechTreeUpgrade = 7003
	FinishVTechTreeUpgrade = 7004
	SummonCommonMount = 8000
	SummonRareMount = 8001
	SummonEpicMount = 8002
	SummonLegendaryMount = 8003
	SummonUltimateMount = 8004
	SummonMythicMount = 8005
	MergeCommonMount = 9000
	MergeRareMount = 9001
	MergeEpicMount = 9002
	MergeLegendaryMount = 9003
	MergeUltimateMount = 9004
	MergeMythicMount = 9005
	CompleteLevel1to10Mission = 10000
	CompleteLevel11to20Mission = 10001
	CompleteLevel21to30Mission = 10002
	CompleteLevel31to40Mission = 10003
	CompleteLevel41to50Mission = 10004
	CompleteLevel51to60Mission = 10005

class DailyDealType(IntEnum):
	Dungeon = 0
	Resource = 1
	Pet = 2
	Skill = 3
	Tech = 4
	Mount = 5

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


class GemSkipTarget(IntEnum):
	Forge = 0
	PetEgg = 1
	TechTree = 2


@miraesee_extension
class ItemAge(IntEnum):
	Primitive = 0
	Medieval = 1
	EarlyModern = 2
	Modern = 3
	Space = 4
	Interstellar = 5
	Multiverse = 6
	Quantum = 7
	Underworld = 8
	Divine = 9
	DefaultWeapon = 10000

class ItemType(IntEnum):
	Helmet = 0
	Armour = 1
	Gloves = 2
	Necklace = 3
	Ring = 4
	Weapon = 5
	Shoes = 6
	Belt = 7

class PetBalancingType(IntEnum):
	Balanced = 0
	Damage = 1
	Health = 2

class PvpBattleType(IntEnum):
	Test = 0
	Chat = 1
	ChatReplay = 2
	Arena = 3
	GuildWar = 4

class PvpBattleState(IntEnum):
	None_ = 0
	Running = 1
	CombatFinished = 2
	Finished = 3

class PvpBattleResult(IntEnum):
	NotFinished = 0
	Draw = 1
	Party1Win = 2
	Party2Win = 3
	Forfeit = 4

class Rarity(IntEnum):
	Common = 0
	Rare = 1
	Epic = 2
	Legendary = 3
	Ultimate = 4
	Mythic = 5

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

class StatLayer(IntEnum):
	None_ = 0
	GeneralCompounding = 1
	Skins = 2
	Ascensions = 3
	TechTree = 4

class StatCondition(IntEnum):
	None_ = 0
	Melee = 1
	Ranged = 2

class StatTargetKind(IntEnum):
	Player = 0
	Equipment = 1
	ActiveSkill = 2
	PassiveSkill = 3
	Mount = 4
	Forge = 5
	Egg = 6
	Currency = 7
	Pet = 8
	TechTree = 9
	Duration = 10

class StatQualifierType(IntEnum):
	ItemType = 0
	AttackType = 1
	Rarity = 2
	Skill = 3
	CurrencyType = 4
	DungeonType = 5
	Source = 6

class Source(IntEnum):
	Offline = 0

class StatType(IntEnum):
	Damage = 0
	Health = 1
	MaxLevel = 2
	Experience = 3
	Cost = 4
	TimerSpeed = 5
	SellPrice = 6
	MaxCount = 7
	Bonus = 8
	FreebieChance = 10
	CriticalChance = 11
	CriticalDamage = 12
	BlockChance = 13
	HealthRegen = 14
	LifeSteal = 15
	DoubleDamageChance = 16
	AttackSpeed = 17
	MoveSpeed = 18

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
	
class TechTreeType(IntEnum):
	Forge = 0
	Power = 1
	SkillsPetTech = 2
	Clan = 3

class Month(IntEnum):
	January = 1
	February = 2
	March = 3
	April = 4
	May = 5
	June = 6
	July = 7
	August = 8
	September = 9
	October = 10
	November = 11
	December = 12

class SteppingStoneEndReason(IntEnum):
	Fell = 0
	ReachedEnd = 1
