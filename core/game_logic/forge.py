# core/game_logic/forge.py
"""
Forge simulation.

Per hammer: RandomPCG(forge_seed), then forge_seed += 1.
All catalog keys use ItemType enum (not strings).
Round-robin filters the item pool before next_int(len); state must advance each pull.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from config import (
	FORGE_CONFIG,
	ITEM_AGE_DROP_CHANCES_LIBRARY,
	ITEM_BALANCING_LIBRARY,
	SECONDARY_STAT_ITEM_UNLOCK,
	STAT_DISPLAY_NAMES,
	STAT_RANGES,
	WEAPON_LIBRARY,
)
from core.enums import CurrencyType, ItemAge, ItemType, SecondaryStatType, TechTreeNodeType
from core.random_pcg import RandomPCG
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.PlayerModel import PlayerModel
from core.game_logic.player_model.StatModel import StatModel


# ---------------------------------------------------------------------------
# Static catalog (built once at import time from JSON data)
# ---------------------------------------------------------------------------

_TYPE_ORDER: list[ItemType] = [
	ItemType.Helmet,
	ItemType.Armour,
	ItemType.Gloves,
	ItemType.Necklace,
	ItemType.Ring,
	ItemType.Weapon,
	ItemType.Shoes,
	ItemType.Belt,
]

_STAT_POOL: list[str] = list(STAT_RANGES.keys())


def _build_weapon_props() -> dict[tuple[int, int], dict]:
	out: dict[tuple[int, int], dict] = {}
	for entry in WEAPON_LIBRARY.values():
		wid = entry.get("ItemId", {})
		age, idx = wid.get("Age"), wid.get("Idx")
		if age is None or idx is None:
			continue
		out[(int(age), int(idx))] = {
			"is_ranged": int(entry.get("AttackRange", 0)) >= 7,
			"windup": float(entry.get("WindupTime", 0.0)),
		}
	return out


_WEAPON_PROPS: dict[tuple[int, int], dict] = _build_weapon_props()


def _build_catalog() -> dict[ItemType, dict[int, list[dict]]]:
	catalog: dict[ItemType, dict[int, list[dict]]] = {t: {} for t in ItemType}
	for entry in ITEM_BALANCING_LIBRARY.values():
		item_id = entry["ItemId"]
		age = int(item_id["Age"])
		if age > 9:
			continue
		try:
			item_type = ItemType[item_id["Type"]]
		except KeyError:
			continue
		idx = int(item_id.get("Idx", 0))
		row: dict = {
			"age": age,
			"item_type": item_type,
			"idx": idx,
			"item_id": item_id,
			"data": entry,
		}
		if item_type is ItemType.Weapon:
			props = _WEAPON_PROPS.get((age, idx), {})
			row["is_ranged"] = props.get("is_ranged", False)
			row["windup"] = props.get("windup", 0.0)
		catalog[item_type].setdefault(age, []).append(row)
	for itype in catalog:
		for age in catalog[itype]:
			catalog[itype][age].sort(key=lambda r: r["idx"])
	return catalog


_CATALOG: dict[ItemType, dict[int, list[dict]]] = _build_catalog()


# ---------------------------------------------------------------------------
# Logic helpers (private)
# ---------------------------------------------------------------------------

def _get_free_forge_chance_pct(player: PlayerModel) -> float:
	"""FreeForgeChance: +1% per research level, capped at 25."""
	level = min(25, player.get_tech_level(TechTreeNodeType.FreeForgeChance))
	return float(level)


def _roll_age(player: PlayerModel, rng: RandomPCG) -> int:
	"""next_f64 cumulative; forge_level key is (UI level - 1)."""
	level_key = str(max(0, player.forge.forge_level - 1))
	row = ITEM_AGE_DROP_CHANCES_LIBRARY.get(
		level_key,
		ITEM_AGE_DROP_CHANCES_LIBRARY.get(str(player.forge.forge_level), {}),
	)
	roll = rng.next_f64()
	acc = 0.0
	for age in range(10):
		acc += float(row.get(f"Age{age}", 0.0))
		if roll < acc:
			return age
	return 0


def _available_types(age: int) -> list[ItemType]:
	return [t for t in _TYPE_ORDER if age in _CATALOG[t]]


def _pick_item_type(age: int, rng: RandomPCG) -> ItemType | None:
	types = _available_types(age)
	if not types:
		return None
	chosen = types[0]
	count = 0
	for t in types:
		count += 1
		if rng.next_int(count) == 0:
			chosen = t
	return chosen


def _filter_pool(player: PlayerModel, item_type: ItemType, age: int) -> list[dict]:
	pool = list(_CATALOG[item_type].get(age, []))
	used = player.equipment.get_round_robin_indices(item_type, age)
	if not used:
		return pool
	filtered = [row for row in pool if row["idx"] not in used]
	if filtered:
		return filtered
	player.equipment.reset_round_robin(item_type, age)
	return pool


def _stat_count(player: PlayerModel, age: int) -> int:
	num = int(SECONDARY_STAT_ITEM_UNLOCK.get(str(age), {}).get("NumberOfSecondStats", 0))
	if player.forge.ascension_model.current_level >= 1:
		num = max(2, num)
	return num


def _roll_secondary_stats(chosen: dict, rng: RandomPCG, num_subs: int) -> list[StatModel]:
	if num_subs <= 0:
		return []
	pool = list(_STAT_POOL)
	if chosen["item_type"] is ItemType.Weapon:
		if chosen.get("is_ranged", False):
			pool = [s for s in pool if s != "MeleeDamageMulti"]
		else:
			pool = [s for s in pool if s != "RangedDamageMulti"]
	stats: list[StatModel] = []
	for _ in range(num_subs):
		if not pool:
			break
		name = pool.pop(rng.next_int(len(pool)))
		f64 = rng.next_f64()
		stats.append(StatModel(SecondaryStatType[name], f64))
	return stats


def _simulate_pull(
	player: PlayerModel,
	seed: int,
	free_chance_pct: float,
) -> tuple[ItemModel | None, bool]:
	"""
	One forge pull -- same RNG order as the validated reference.
	Returns (item, is_free_forge).
	"""
	rng = RandomPCG(seed)

	rolled_age = _roll_age(player, rng)
	item_type = _pick_item_type(rolled_age, rng)
	if item_type is None:
		return None, False

	rng.next_guid()

	pool = _filter_pool(player, item_type, rolled_age)
	if not pool:
		return None, False

	chosen = pool[rng.next_int(len(pool))]
	_ = rng.next_int(100)

	num_subs = _stat_count(player, rolled_age)
	stat_models = _roll_secondary_stats(chosen, rng, num_subs)

	is_free = rng.next_f64() < (free_chance_pct / 100.0)

	item = ItemModel(ItemAge(rolled_age), item_type, chosen["idx"])
	item.is_newly_forged = True
	item.is_free_forge = is_free
	item.guid = f"{seed:016X}-SIM"
	for stat in stat_models:
		item.secondary_stats.add_stat(stat)

	player.equipment.add_round_robin_index(item_type, rolled_age, chosen["idx"])
	if rolled_age > player.forge.max_forged_age:
		player.forge.max_forged_age = rolled_age

	return item, is_free


# ---------------------------------------------------------------------------
# Public result types
# ---------------------------------------------------------------------------

@dataclass
class ForgePullResult:
	item:          ItemModel
	is_free_forge: bool
	seed_used:     int


@dataclass
class ForgeResult:
	requested_hammers: int
	actual_hammers:    int
	pulls:             list[ForgePullResult] = field(default_factory=list)
	free_forge_count:  int                  = 0
	success:           bool                 = True
	error:             str | None           = None


# ---------------------------------------------------------------------------
# ForgeSimulator
# ---------------------------------------------------------------------------

class ForgeSimulator:
	"""
	Drives the forge loop for a given PlayerModel.
	Call forge(n) to simulate n hammer uses.
	"""

	def __init__(self, player: PlayerModel) -> None:
		self.player = player

	def forge(self, hammer_count: int) -> ForgeResult:
		if hammer_count < 1:
			return ForgeResult(0, 0, success=False, error="invalid_hammer_count")

		cost_per = int(FORGE_CONFIG.get("ForgeCost", 1))
		total_cost = hammer_count * cost_per
		if self.player.get_currency(CurrencyType.Hammers) < total_cost:
			return ForgeResult(hammer_count, 0, success=False, error="insufficient_hammers")

		self.player.sub_currency(CurrencyType.Hammers, total_cost)

		free_pct = _get_free_forge_chance_pct(self.player)
		pulls: list[ForgePullResult] = []
		free_count = 0

		for _ in range(hammer_count):
			seed = self.player.forge.forge_seed
			item, is_free = _simulate_pull(self.player, seed, free_pct)
			if item is None:
				return ForgeResult(
					hammer_count,
					len(pulls),
					pulls=pulls,
					success=False,
					error="forge_pull_failed",
				)
			self.player.forge.pending_items.insert(0, item)
			pulls.append(ForgePullResult(item=item, is_free_forge=is_free, seed_used=seed))
			if is_free:
				free_count += 1
			self.player.forge.forge_seed = seed + 1

		return ForgeResult(
			requested_hammers=hammer_count,
			actual_hammers=len(pulls),
			pulls=pulls,
			free_forge_count=free_count,
		)

	def format_pull(self, pull: ForgePullResult, index: int) -> str:
		item = pull.item
		stat_parts = []
		for s in item.secondary_stats.stats:
			label = STAT_DISPLAY_NAMES.get(s.stat_type.name, s.stat_type.name)
			val_pct = s.value * 100.0
			stat_parts.append(f"{label}({val_pct:+.2f}%)")
		perf = item.secondary_stats.perfection * 100.0
		free = " FREE" if pull.is_free_forge else ""
		return (
			f"#{index:>3} seed={pull.seed_used:#018x}{free} | "
			f"{item.age.name}/{item.item_type.name}/idx{item.idx} | "
			f"perf {perf:.2f}% | {', '.join(stat_parts) or '-'}"
		)
