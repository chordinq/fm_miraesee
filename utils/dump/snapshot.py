from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class SummonMetaDump:
	level: int = 0
	count: int = 0
	seed: int = 0
	ascension_level: int = 0
	hatch_slots_count: int = 0


@dataclass
class ForgeMetaDump:
	forge_level: int = 0
	forge_count: int = 0
	forge_seed: int = 0
	highest_age_of_crafted_item: int = 0
	ascension_level: int = 0
	timer_start_ms: int = 0
	timer_end_ms: int = 0


@dataclass
class SkillEntryDump:
	combat_skill_enum: int
	level: int
	shard_count: int
	is_equipped: bool
	equip_slot: int


@dataclass
class PetEntryDump:
	rarity: int
	pet_id: int
	level: int
	experience: int
	is_equipped: bool
	equip_slot: int
	stats_blob: str
	is_locked: bool = False


@dataclass
class EggEntryDump:
	rarity: int
	is_equipped: bool
	equip_slot: int
	seed: int
	timer_start_ms: int = 0
	timer_end_ms: int = 0


@dataclass
class TechTreeTimerDump:
	tree_type: int
	local_id: int
	timer_start_ms: int
	timer_end_ms: int


@dataclass
class MountEntryDump:
	rarity: int
	mount_id: int
	level: int
	experience: int
	is_equipped: bool
	stats_blob: str
	is_locked: bool = False


@dataclass
class EquipmentItemDump:
	age: int
	item_type: int
	idx: int
	level: int
	stats_blob: str


@dataclass
class HiddenLevelDump:
	item_type: int
	age: int
	level: int


@dataclass
class RoundRobinDump:
	item_type: int
	age: int
	indices: list[int]


@dataclass
class TechTreeNodeDump:
	tree_type: int
	local_id: int
	ui_level: int


@dataclass
class SkinEntryDump:
	"""One PlayerSkinModel entry from the SKIN_COLLECTION dump block.

	Dump line format (35 chars):
	    5 <item_type:1hex> <idx:02hex> <is_eq:1hex> <level:02hex> <exp:08hex> <stats_blob:20hex>
	"""

	item_type: int
	idx: int
	is_equipped: bool
	level: int
	experience: int
	stats_blob: str  # 20-char hex (StatContributions, up to 2 stat chunks)


@dataclass
class DumpSnapshot:
	version: int = 1
	currencies: dict[int, int] = field(default_factory=dict)
	techtree_nodes: list[TechTreeNodeDump] = field(default_factory=list)
	techtree_timers: list[TechTreeTimerDump] = field(default_factory=list)
	forge_meta: ForgeMetaDump | None = None
	skill_summon_meta: SummonMetaDump | None = None
	pet_summon_meta: SummonMetaDump | None = None
	mount_summon_meta: SummonMetaDump | None = None
	skills: list[SkillEntryDump] = field(default_factory=list)
	pets: list[PetEntryDump] = field(default_factory=list)
	eggs: list[EggEntryDump] = field(default_factory=list)
	mounts: list[MountEntryDump] = field(default_factory=list)
	hidden_levels: list[HiddenLevelDump] = field(default_factory=list)
	round_robins: list[RoundRobinDump] = field(default_factory=list)
	equipment_slots: list[EquipmentItemDump] = field(default_factory=list)
	skins: list[SkinEntryDump] = field(default_factory=list)
