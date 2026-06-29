import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

_HATCH_TEST_SLOT = 0


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def _prepare_mixed_hatch_slots(collection) -> tuple[int, int]:
    kept = 0
    cleared = 0
    for egg in collection.eggs:
        if not egg.is_equipped:
            continue
        if egg.equip_slot == _HATCH_TEST_SLOT:
            kept += 1
            continue
        egg.is_equipped = False
        egg.equip_slot = -1
        cleared += 1
    return kept, cleared


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.7, 0.5)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    collection = player.player_pet_collection_model
    kept, cleared = _prepare_mixed_hatch_slots(collection)
    pet_collection_bridge = PetCollectionBridge(collection, player, parent=engine)
    slot_count = pet_collection_bridge.hatchSlotCount
    empty_count = slot_count - kept

    set_window_context(
        engine,
        init_width,
        init_height,
        testPetCollection=pet_collection_bridge,
        hatchTestFilledCount=kept,
        hatchTestEmptyCount=empty_count,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_hatchslot.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({kept} filled, {empty_count} empty / {slot_count} hatch slots, "
        f"dump={DUMP_PATH.name})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
