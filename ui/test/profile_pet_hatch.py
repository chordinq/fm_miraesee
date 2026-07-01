from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import QCoreApplication, QUrl
from PySide6.QtWidgets import QApplication

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.summon.pet_egg_test_bridge import PetEggTestBridge


def _ms(start: float) -> float:
    return (time.perf_counter() - start) * 1000.0


def _first_inventory_egg_guid(collection) -> str:
    for egg in collection.eggs:
        if not egg.is_equipped and egg.hatch_timer_model is None:
            return egg.guid
    raise RuntimeError("no inventory egg in dump")


def profile_headless(dump_path: Path) -> None:
    text = dump_path.read_text(encoding="utf-8")
    t0 = time.perf_counter()
    player = dump_snapshot_to_player_model(parse_dump_text(text))
    print(f"dump parse + player build: {_ms(t0):.1f} ms")

    t0 = time.perf_counter()
    pet_collection = PetCollectionBridge(
        player.player_pet_collection_model,
        player,
    )
    print(
        f"PetCollectionBridge init ({pet_collection.entryCount} grid rows): "
        f"{_ms(t0):.1f} ms"
    )

    logic = GameLogic(player)
    egg_bridge = PetEggTestBridge(logic, pet_collection)
    egg_guid = _first_inventory_egg_guid(player.player_pet_collection_model)
    rows_before = pet_collection.entryCount

    t0 = time.perf_counter()
    slot = 0
    for index in range(player.player_pet_collection_model.unlocked_hatch_slots_count):
        if player.player_pet_collection_model.is_hatch_slot_available(index):
            slot = index
            break
    result = logic.pet_egg_hatch_start(egg_guid, slot, commit=True)
    print(f"core pet_egg_hatch_start: {_ms(t0):.2f} ms ({result.name})")

    t0 = time.perf_counter()
    pet_collection.patch_egg_moved_to_hatch(egg_guid)
    print(
        f"patch_egg_moved_to_hatch ({rows_before} -> {pet_collection.entryCount} rows): "
        f"{_ms(t0):.2f} ms"
    )

    t0 = time.perf_counter()
    egg_bridge.selectEgg(egg_guid)
    print(f"selectEgg (meta only, stat deferred): {_ms(t0):.2f} ms")

    t0 = time.perf_counter()
    egg_bridge._deferred_build_egg_stat_lines()
    print(f"deferred stat lines build: {_ms(t0):.2f} ms")


def profile_qml(dump_path: Path) -> None:
    from app.harness import create_qml_engine, register_qml_services

    app = QApplication.instance()
    if app is None:
        raise RuntimeError("QApplication required for QML profile")

    engine = create_qml_engine()
    register_qml_services(engine)
    text = dump_path.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(text))
    logic = GameLogic(player)
    pet_collection = PetCollectionBridge(
        player.player_pet_collection_model,
        player,
    )
    egg_bridge = PetEggTestBridge(logic, pet_collection)
    egg_guid = _first_inventory_egg_guid(player.player_pet_collection_model)

    engine.rootContext().setContextProperty("petCollectionModel", pet_collection)
    engine.load(QUrl.fromLocalFile(str(ROOT / "ui" / "test" / "profile_pet_slot_grid.qml")))
    if not engine.rootObjects():
        raise RuntimeError("failed to load profile_pet_slot_grid.qml")

    t0 = time.perf_counter()
    app.processEvents()
    print(f"QML initial processEvents: {_ms(t0):.1f} ms")

    t0 = time.perf_counter()
    egg_bridge.selectEgg(egg_guid)
    app.processEvents()
    print(f"selectEgg + processEvents: {_ms(t0):.1f} ms")

    slot = next(
        index
        for index in range(player.player_pet_collection_model.unlocked_hatch_slots_count)
        if player.player_pet_collection_model.is_hatch_slot_available(index)
    )
    t0 = time.perf_counter()
    logic.pet_egg_hatch_start(egg_guid, slot, commit=True)
    pet_collection.patch_egg_moved_to_hatch(egg_guid)
    app.processEvents()
    print(f"hatch start + patch + processEvents: {_ms(t0):.1f} ms")


def main() -> None:
    dump_path = ROOT / "ui" / "test" / "fixtures" / "test_user_dump.txt"
    if not dump_path.exists():
        print(f"dump fixture missing: {dump_path}")
        sys.exit(1)

    use_qml = "--qml" in sys.argv
    if use_qml:
        app = QApplication(sys.argv)
    else:
        app = QCoreApplication(sys.argv)

    preview_player = dump_snapshot_to_player_model(
        parse_dump_text(dump_path.read_text(encoding="utf-8"))
    )
    pet_count = len(preview_player.player_pet_collection_model.pets)
    egg_count = len(preview_player.player_pet_collection_model.eggs)
    print(f"fixture: {pet_count} pets, {egg_count} eggs\n--- headless ---")
    profile_headless(dump_path)

    if use_qml:
        print("\n--- qml ---")
        profile_qml(dump_path)

    del app


if __name__ == "__main__":
    main()
