from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional
from ..enums import (
	AttackType,
	CombatSkill,
	CurrencyType,
	DungeonType,
	ItemType,
	Rarity,
	Source,
	StatCondition,
	StatLayer,
	StatQualifierType,
	StatTargetKind,
)

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


@dataclass(frozen=True)
class StatQualifier:
	type: StatQualifierType
	value: int

	def __post_init__(self) -> None:
		object.__setattr__(self, "type", StatQualifierType(self.type))
		object.__setattr__(self, "value", int(self.value))


@dataclass(frozen=True)
class StatTarget:
	kind: StatTargetKind
	qualifiers: tuple[StatQualifier, ...] = ()

	def __post_init__(self) -> None:
		object.__setattr__(self, "kind", StatTargetKind(self.kind))
		if not isinstance(self.qualifiers, tuple):
			object.__setattr__(self, "qualifiers", tuple(self.qualifiers))

	@staticmethod
	def player() -> StatTarget:
		return StatTarget(StatTargetKind.Player)

	@staticmethod
	def equipment() -> StatTarget:
		return StatTarget(StatTargetKind.Equipment)

	@staticmethod
	def active_skill() -> StatTarget:
		return StatTarget(StatTargetKind.ActiveSkill)

	@staticmethod
	def passive_skill() -> StatTarget:
		return StatTarget(StatTargetKind.PassiveSkill)

	@staticmethod
	def mount() -> StatTarget:
		return StatTarget(StatTargetKind.Mount)

	@staticmethod
	def forge() -> StatTarget:
		return StatTarget(StatTargetKind.Forge)

	@staticmethod
	def egg() -> StatTarget:
		return StatTarget(StatTargetKind.Egg)

	@staticmethod
	def pet() -> StatTarget:
		return StatTarget(StatTargetKind.Pet)

	@staticmethod
	def currency() -> StatTarget:
		return StatTarget(StatTargetKind.Currency)

	@staticmethod
	def tech_tree() -> StatTarget:
		return StatTarget(StatTargetKind.TechTree)

	@staticmethod
	def duration() -> StatTarget:
		return StatTarget(StatTargetKind.Duration)

	def _add_qualifier(self, qualifier_type: StatQualifierType, value: int) -> StatTarget:
		return StatTarget(
			self.kind,
			self.qualifiers + (StatQualifier(qualifier_type, value),),
		)

	def with_item_type(self, item_type: ItemType) -> StatTarget:
		return self._add_qualifier(StatQualifierType.ItemType, int(item_type))

	def with_attack_type(self, attack_type: AttackType) -> StatTarget:
		return self._add_qualifier(StatQualifierType.AttackType, int(attack_type))

	def with_rarity(self, rarity: Rarity) -> StatTarget:
		return self._add_qualifier(StatQualifierType.Rarity, int(rarity))

	def with_skill(self, skill: CombatSkill) -> StatTarget:
		return self._add_qualifier(StatQualifierType.Skill, int(skill))

	def with_currency(self, currency_type: CurrencyType) -> StatTarget:
		return self._add_qualifier(StatQualifierType.CurrencyType, int(currency_type))

	def with_dungeon_type(self, dungeon_type: DungeonType) -> StatTarget:
		return self._add_qualifier(StatQualifierType.DungeonType, int(dungeon_type))

	def with_source(self, source: Source) -> StatTarget:
		return self._add_qualifier(StatQualifierType.Source, int(source))

	def equals(self, other: StatTarget | None) -> bool:
		if other is None:
			return False
		if self is other:
			return True
		if self.kind != other.kind:
			return False
		if len(self.qualifiers) != len(other.qualifiers):
			return False
		for left, right in zip(self.qualifiers, other.qualifiers):
			if left != right:
				return False
		return True

	def get_dependencies(self) -> list[StatTarget]:
		count = len(self.qualifiers)
		if count == 0:
			return []
		dependencies: list[StatTarget] = []
		for index in range(count):
			prefix_len = count - 1 - index
			if prefix_len <= 0:
				dependencies.append(StatTarget(self.kind))
			else:
				dependencies.append(StatTarget(self.kind, self.qualifiers[:prefix_len]))
		return dependencies

	@staticmethod
	def from_legacy(
		legacy: StatTargetBase,
	) -> tuple[StatTarget, StatLayer, StatCondition]:
		from ..enums import ItemType, Source, StatCondition, StatLayer

		if isinstance(legacy, PlayerStatTarget):
			return StatTarget.player(), StatLayer.None_, StatCondition.None_
		if isinstance(legacy, PlayerMeleeOnlyStatTarget):
			return StatTarget.player(), StatLayer.None_, StatCondition.Melee
		if isinstance(legacy, PlayerRangedOnlyStatTarget):
			return StatTarget.player(), StatLayer.None_, StatCondition.Ranged
		if isinstance(legacy, PlayerSkinMultiplierStatTarget):
			return StatTarget.player(), StatLayer.Skins, StatCondition.None_
		if isinstance(legacy, EquipmentStatTarget):
			target = StatTarget.equipment()
			if legacy.item_type is not None:
				target = target.with_item_type(legacy.item_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, WeaponStatTarget):
			target = StatTarget.equipment().with_item_type(ItemType.Weapon)
			if legacy.attack_type is not None:
				target = target.with_attack_type(legacy.attack_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, ActiveSkillStatTarget):
			target = StatTarget.active_skill()
			if legacy.skill_type is not None:
				target = target.with_skill(legacy.skill_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, PassiveSkillStatTarget):
			target = StatTarget.passive_skill()
			if legacy.skill_type is not None:
				target = target.with_skill(legacy.skill_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, MountStatTarget):
			target = StatTarget.mount()
			if legacy.mount_rarity is not None:
				target = target.with_rarity(legacy.mount_rarity)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, PetStatTarget):
			target = StatTarget.pet()
			if legacy.pet_rarity is not None:
				target = target.with_rarity(legacy.pet_rarity)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, EggStatTarget):
			target = StatTarget.egg()
			if legacy.egg_rarity is not None:
				target = target.with_rarity(legacy.egg_rarity)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, ForgeStatTarget):
			return StatTarget.forge(), StatLayer.None_, StatCondition.None_
		if isinstance(legacy, TechTreeStatTarget):
			return StatTarget.tech_tree(), StatLayer.None_, StatCondition.None_
		if isinstance(legacy, OfflineTimerStatTarget):
			return (
				StatTarget.duration().with_source(Source.Offline),
				StatLayer.None_,
				StatCondition.None_,
			)
		if isinstance(legacy, OfflineCurrencyStatTarget):
			target = StatTarget.currency().with_source(Source.Offline)
			if legacy.currency_type is not None:
				target = target.with_currency(legacy.currency_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, CurrencyBonusStatTarget):
			target = StatTarget.currency()
			if legacy.currency_type is not None:
				target = target.with_currency(legacy.currency_type)
			return target, StatLayer.None_, StatCondition.None_
		if isinstance(legacy, DungeonStatTarget):
			target = StatTarget.currency()
			if legacy.dungeon_type is not None:
				target = target.with_dungeon_type(legacy.dungeon_type)
			if legacy.currency_type is not None:
				target = target.with_currency(legacy.currency_type)
			return target, StatLayer.None_, StatCondition.None_
		raise ValueError(f"Unknown StatTargetBase type: {type(legacy)!r}")
