from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from .enums import ItemType, AttackType, CombatSkill, Rarity, CurrencyType, DungeonType

class StatTargetBase(ABC):
	@abstractmethod
	def __str__(self) -> str:
		pass


@dataclass(frozen=True)
class PlayerStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "PlayerStatTarget"


@dataclass(frozen=True)
class PlayerRangedOnlyStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "PlayerRangedOnlyStatTarget"


@dataclass(frozen=True)
class PlayerMeleeOnlyStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "PlayerMeleeOnlyStatTarget"


@dataclass(frozen=True)
class PlayerSkinMultiplierStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "PlayerSkinMultiplierStatTarget"


@dataclass(frozen=True)
class EquipmentStatTarget(StatTargetBase):
	item_type: Optional[ItemType] = None
	def __str__(self) -> str:
		item_type_str = self.item_type.name if self.item_type is not None else "All"
		return f"EquipmentStatTarget_{item_type_str}"


@dataclass(frozen=True)
class WeaponStatTarget(StatTargetBase):
	attack_type: Optional[AttackType] = None
	def __str__(self) -> str:
		attack_type_str = self.attack_type.name if self.attack_type is not None else "All"
		return f"WeaponStatTarget_{attack_type_str}"


@dataclass(frozen=True)
class ActiveSkillStatTarget(StatTargetBase):
	skill_type: Optional[CombatSkill] = None
	def __str__(self) -> str:
		skill_type_str = self.skill_type.name if self.skill_type is not None else "All"
		return f"ActiveSkillStatTarget_{skill_type_str}"


@dataclass(frozen=True)
class PassiveSkillStatTarget(StatTargetBase):
	skill_type: Optional[CombatSkill] = None
	def __str__(self) -> str:
		skill_type_str = self.skill_type.name if self.skill_type is not None else "All"
		return f"PassiveSkillStatTarget_{skill_type_str}"


@dataclass(frozen=True)
class MountStatTarget(StatTargetBase):
	mount_rarity: Optional[Rarity] = None
	def __str__(self) -> str:
		mount_rarity_str = self.mount_rarity.name if self.mount_rarity is not None else "All"
		return f"MountStatTarget_{mount_rarity_str}"


@dataclass(frozen=True)
class ForgeStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "ForgeStatTarget"


@dataclass(frozen=True)
class EggStatTarget(StatTargetBase):
	egg_rarity: Optional[Rarity] = None
	def __str__(self) -> str:
		egg_rarity_str = self.egg_rarity.name if self.egg_rarity is not None else "All"
		return f"EggStatTarget_{egg_rarity_str}"


@dataclass(frozen=True)
class CurrencyBonusStatTarget(StatTargetBase):
	currency_type: Optional[CurrencyType] = None
	def __str__(self) -> str:
		currency_type_str = self.currency_type.name if self.currency_type is not None else "All"
		return f"CurrencyBonusStatTarget_{currency_type_str}"


@dataclass(frozen=True)
class OfflineTimerStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "OfflineTimerStatTarget"


@dataclass(frozen=True)
class OfflineCurrencyStatTarget(StatTargetBase):
	currency_type: Optional[CurrencyType] = None
	def __str__(self) -> str:
		currency_type_str = self.currency_type.name if self.currency_type is not None else "All"
		return f"OfflineCurrencyStatTarget_{currency_type_str}"


@dataclass(frozen=True)
class DungeonStatTarget(StatTargetBase):
	dungeon_type: Optional[DungeonType] = None
	currency_type: Optional[CurrencyType] = None
	def __str__(self) -> str:
		dungeon_type_str = self.dungeon_type.name if self.dungeon_type is not None else "All"
		currency_type_str = self.currency_type.name if self.currency_type is not None else "All"
		return f"DungeonStatTarget_{dungeon_type_str}_{currency_type_str}"


@dataclass(frozen=True)
class PetStatTarget(StatTargetBase):
	pet_rarity: Optional[Rarity] = None
	def __str__(self) -> str:
		pet_rarity_str = self.pet_rarity.name if self.pet_rarity is not None else "All"
		return f"PetStatTarget_{pet_rarity_str}"


@dataclass(frozen=True)
class TechTreeStatTarget(StatTargetBase):
	def __str__(self) -> str:
		return "TechTreeStatTarget"
