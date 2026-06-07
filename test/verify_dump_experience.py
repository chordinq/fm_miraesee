"""Load test_user_dump.txt and verify pet/mount XP helpers + stats."""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
	sys.path.insert(0, str(_ROOT))

from core.game_logic.player.player_mount_collection_model import PlayerMountModel
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
from core.game_logic.stats.pet_stats import format_pet_stat_display, resolve_pet_primary_stats
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def main() -> None:
	dump_path = _ROOT / "test_user_dump.txt"
	text = dump_path.read_text(encoding="utf-8")
	snap = parse_dump_text(text)
	player = dump_snapshot_to_player_model(snap)
	pc = player.player_pet_collection_model
	mc = player.player_mount_collection_model

	print("=== Summon meta ===")
	if snap.pet_summon_meta:
		m = snap.pet_summon_meta
		print(
			f"Pet summon: level={m.level} count={m.count} "
			f"seed={m.seed:#018x} asc={m.ascension_level}"
		)
	if snap.mount_summon_meta:
		m = snap.mount_summon_meta
		print(
			f"Mount summon: level={m.level} count={m.count} "
			f"seed={m.seed:#018x} asc={m.ascension_level}"
		)

	print()
	print(f"=== Pets ({len(pc.pets)}) ===")
	all_ok = True
	for i, pet in enumerate(pc.pets):
		total = pet.get_total_xp(player)
		lvl2, rem2 = PlayerPetModel.calculate_level_and_xp(player, pet, total)
		dmg, hp = resolve_pet_primary_stats(player, pet)
		ok = lvl2 == pet.level and rem2 == pet.experience
		all_ok &= ok
		status = "OK" if ok else "MISMATCH"
		print(
			f"  [{i}] {pet.pet_id.rarity.name} id={pet.pet_id.id} "
			f"L={pet.level} xp={pet.experience} total={total} "
			f"roundtrip={lvl2}/{rem2} {status}"
		)
		print(
			f"       dmg={format_pet_stat_display(dmg)} "
			f"hp={format_pet_stat_display(hp)} "
			f"eq={pet.is_equipped} slot={pet.equip_slot}"
		)

	print()
	print(f"=== Eggs ({len(pc.eggs)}) ===")
	for i, egg in enumerate(pc.eggs):
		xp = egg.get_xp(player)
		print(
			f"  [{i}] {egg.rarity.name} seed={egg.seed:#018x} "
			f"hatch_xp={xp} eq={egg.is_equipped} slot={egg.equip_slot}"
		)

	print()
	print(f"=== Mounts ({len(mc.player_mount_models)}) ===")
	for i, mount in enumerate(mc.player_mount_models):
		total = mount.get_total_xp(player)
		lvl2, rem2 = PlayerMountModel.calculate_level_and_xp(player, mount, total)
		ok = lvl2 == mount.level and rem2 == mount.experience
		all_ok &= ok
		status = "OK" if ok else "MISMATCH"
		print(
			f"  [{i}] {mount.mount_id.rarity.name} id={mount.mount_id.id} "
			f"L={mount.level} xp={mount.experience} total={total} "
			f"roundtrip={lvl2}/{rem2} {status} eq={mount.is_equipped}"
		)

	print()
	if all_ok:
		print("All XP roundtrips passed.")
	else:
		print("Some XP roundtrips FAILED.")
		sys.exit(1)


if __name__ == "__main__":
	main()
