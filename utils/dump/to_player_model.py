from __future__ import annotations

from config import SKILLS_MAPPING
from core.game_logic.enums import (
	CombatSkill,
	CurrencyType,
	ItemAge,
	ItemType,
	Rarity,
	TechTreeType,
)
from core.game_logic.player.player_equipment_model import ItemModel, PlayerEquipmentModel
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.config.shared_game_config import get_shared_game_config
from core.game_logic.player.player_mount_collection_model import MountId, PlayerMountModel
from core.game_logic.player.player_pet_collection_model import PetId, PlayerEggModel, PlayerPetModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.player.player_skin_collection_model import PlayerSkinModel, SkinId
from core.game_logic.player.timer_model import TimerModel

from .parser import _TECHTREE_LOOKUP
from .schema import EMPTY_EQUIP_SLOT, EQUIPMENT_STATS_LEN
from .snapshot import DumpSnapshot
from .stats_blob import parse_stats_blob

_EQUIPMENT_SLOT_FIELDS = (
	"helmet",
	"armour",
	"gloves",
	"necklace",
	"ring",
	"weapon",
	"shoes",
	"belt",
)

_EMPTY_SLOT = -1


def _timer_from_epoch_ms(start_ms: int, end_ms: int) -> TimerModel | None:
	if start_ms <= 0 or end_ms <= start_ms:
		return None
	start_s = start_ms // 1000
	end_s = end_ms // 1000
	duration = float(end_s - start_s)
	return TimerModel(start_time=start_s, end_time=end_s, duration=duration)


def _resolve_combat_skill(enum_value: int) -> CombatSkill | None:
	# Lua exports CombatSkill enum as s_enum; Skills_Mapping.json uses "Type" (no "Enum" key).
	try:
		return CombatSkill(enum_value)
	except ValueError:
		pass
	for data in SKILLS_MAPPING.values():
		if data.get("Type") == enum_value:
			return CombatSkill(int(data["Type"]))
	return None


def _normalize_equip_slot(is_equipped: bool, slot: int) -> int:
	if not is_equipped:
		return _EMPTY_SLOT
	return slot if slot != EMPTY_EQUIP_SLOT else _EMPTY_SLOT


def dump_snapshot_to_player_model(snapshot: DumpSnapshot) -> PlayerModel:
	player = PlayerModel(game_config=get_shared_game_config())
	_apply_currency(player, snapshot)
	_apply_techtree(player, snapshot)
	_apply_techtree_timers(player, snapshot)
	_apply_forge_meta(player, snapshot)
	_apply_summon_metas(player, snapshot)
	_apply_skills(player, snapshot)
	_apply_pets_and_eggs(player, snapshot)
	_apply_pet_hatch_slots(player, snapshot)
	_apply_mounts(player, snapshot)
	_apply_equipment_meta(player, snapshot)
	_apply_equipment(player, snapshot)
	_apply_skins(player, snapshot)
	player.enable_wall_clock_server_time()
	return player


def _apply_currency(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	for idx, amount in snapshot.currencies.items():
		try:
			currency = CurrencyType(idx)
		except ValueError:
			continue
		player.player_currency_model.set_currency(currency, amount)


def _apply_techtree(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	for node in snapshot.techtree_nodes:
		if _TECHTREE_LOOKUP.get((node.tree_type, node.local_id)) is None:
			continue
		try:
			tree_type = TechTreeType(node.tree_type)
		except ValueError:
			continue
		internal_level = node.ui_level - 1
		player.player_techtree_model.set_node_level(
			tree_type, node.local_id, internal_level
		)


def _apply_techtree_timers(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	for entry in snapshot.techtree_timers:
		if _TECHTREE_LOOKUP.get((entry.tree_type, entry.local_id)) is None:
			continue
		try:
			tree_type = TechTreeType(entry.tree_type)
		except ValueError:
			continue
		node = player.player_techtree_model.get_node(tree_type, entry.local_id)
		if node is None:
			continue
		timer = _timer_from_epoch_ms(entry.timer_start_ms, entry.timer_end_ms)
		if timer is not None:
			node.node_upgrade_timer_model = timer


def _apply_forge_meta(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	if snapshot.forge_meta is None:
		return
	meta = snapshot.forge_meta
	player.player_forge_model.forge_count = meta.forge_count
	player.player_forge_model.forge_level = meta.forge_level
	player.player_forge_model.forge_seed = meta.forge_seed
	player.player_forge_model.highest_age_of_crafted_item = meta.highest_age_of_crafted_item
	player.player_forge_model.ascension_model.current_level = meta.ascension_level
	timer = _timer_from_epoch_ms(meta.timer_start_ms, meta.timer_end_ms)
	if timer is not None:
		player.player_forge_model.forge_upgrade_timer = timer


def _apply_summon_meta(target, meta) -> None:
	target.summon_model.level = meta.level
	target.summon_model.count = meta.count
	target.summon_model.seed = meta.seed
	target.ascension_model.current_level = meta.ascension_level


def _apply_summon_metas(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	if snapshot.skill_summon_meta:
		_apply_summon_meta(player.player_skill_collection_model, snapshot.skill_summon_meta)
	if snapshot.pet_summon_meta:
		_apply_summon_meta(player.player_pet_collection_model, snapshot.pet_summon_meta)
	if snapshot.mount_summon_meta:
		_apply_summon_meta(player.player_mount_collection_model, snapshot.mount_summon_meta)


def _apply_skills(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	collection = player.player_skill_collection_model
	for entry in snapshot.skills:
		combat_skill = _resolve_combat_skill(entry.combat_skill_enum)
		if combat_skill is None:
			continue
		skill = PlayerSkillModel(combat_skill)
		skill.is_equipped = entry.is_equipped
		skill.equip_slot = _normalize_equip_slot(entry.is_equipped, entry.equip_slot)
		skill.shard_count = entry.shard_count
		skill.level = entry.level
		collection.player_skills[combat_skill] = skill


def _apply_pets_and_eggs(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	collection = player.player_pet_collection_model
	for i, entry in enumerate(snapshot.pets):
		try:
			rarity = Rarity(entry.rarity)
		except ValueError:
			continue
		pet_id = PetId(rarity, entry.pet_id)
		stats = parse_stats_blob(entry.stats_blob)
		pet = PlayerPetModel(f"dump-pet-{i}", pet_id, stats)
		pet.level = entry.level
		pet.experience = entry.experience
		pet.is_equipped = entry.is_equipped
		pet.equip_slot = _normalize_equip_slot(entry.is_equipped, entry.equip_slot)
		pet.is_locked = entry.is_locked
		collection.pets.append(pet)

	for i, entry in enumerate(snapshot.eggs):
		try:
			rarity = Rarity(entry.rarity)
		except ValueError:
			continue
		egg = PlayerEggModel(f"dump-egg-{i}", rarity, entry.seed)
		egg.is_equipped = entry.is_equipped
		egg.equip_slot = _normalize_equip_slot(entry.is_equipped, entry.equip_slot)
		timer = _timer_from_epoch_ms(entry.timer_start_ms, entry.timer_end_ms)
		if timer is not None:
			egg.hatch_timer_model = timer
		collection.eggs.append(egg)


def _apply_pet_hatch_slots(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	collection = player.player_pet_collection_model
	meta = snapshot.pet_summon_meta
	if meta and meta.hatch_slots_count > 0:
		collection.unlocked_hatch_slots_count = meta.hatch_slots_count
		return
	max_slot = _EMPTY_SLOT
	for entry in snapshot.eggs:
		if entry.is_equipped:
			max_slot = max(max_slot, entry.equip_slot)
	if max_slot >= 0:
		collection.unlocked_hatch_slots_count = max_slot + 1


def _apply_mounts(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	collection = player.player_mount_collection_model
	for i, entry in enumerate(snapshot.mounts):
		try:
			rarity = Rarity(entry.rarity)
		except ValueError:
			continue
		mount_id = MountId(rarity, entry.mount_id)
		stats = parse_stats_blob(entry.stats_blob)
		mount = PlayerMountModel(f"dump-mount-{i}", mount_id, stats)
		mount.level = entry.level
		mount.experience = entry.experience
		mount.is_equipped = entry.is_equipped
		mount.is_locked = entry.is_locked
		collection.player_mount_models.append(mount)


def _apply_equipment_meta(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	equip = player.player_equipment_model
	for entry in snapshot.hidden_levels:
		try:
			item_type = ItemType(entry.item_type)
		except ValueError:
			continue
		equip.set_hidden_level(item_type, entry.age, entry.level)

	for entry in snapshot.round_robins:
		try:
			item_type = ItemType(entry.item_type)
		except ValueError:
			continue
		equip.set_round_robin(item_type, entry.age, entry.indices)


def _apply_equipment(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	equip = player.player_equipment_model
	for slot_idx, entry in enumerate(snapshot.equipment_slots):
		if slot_idx >= len(_EQUIPMENT_SLOT_FIELDS):
			break
		try:
			age = ItemAge(entry.age)
			item_type = ItemType(entry.item_type)
		except ValueError:
			continue
		item = ItemModel(age, item_type, entry.idx, level=entry.level)
		item.secondary_stats = parse_stats_blob(
			entry.stats_blob,
			max_stats=EQUIPMENT_STATS_LEN // 10,
		)
		equip.set_item_at_slot(slot_idx, item)


def parse_dump(text: str) -> PlayerModel:
	from .parser import parse_dump_text

	return dump_snapshot_to_player_model(parse_dump_text(text))


def _apply_skins(player: PlayerModel, snapshot: DumpSnapshot) -> None:
	"""Populate PlayerSkinCollectionModel from parsed SkinEntryDump list."""
	collection = player.player_skin_collection_model
	for entry in snapshot.skins:
		try:
			item_type = ItemType(entry.item_type)
		except ValueError:
			continue
		skin_id = SkinId(item_type=item_type, idx=entry.idx)
		skin = PlayerSkinModel(
			skin_id=skin_id,
			level=entry.level,
			experience=entry.experience,
			stats_blob=entry.stats_blob,
			is_equipped=entry.is_equipped,
		)
		if item_type not in collection.skins:
			collection.skins[item_type] = []
		collection.skins[item_type].append(skin)
