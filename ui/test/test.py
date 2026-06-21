import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from pet_collection_bridge import PetCollectionBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

TEST_SUMMON_COUNT = 5
TEST_SUMMON_COST = 176


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.6, 0.75)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    pet_bridge = PetCollectionBridge(
        player.player_pet_collection_model,
        parent=engine,
    )

    set_window_context(
        engine,
        init_width,
        init_height,
        testPetCollection=pet_bridge,
        testSummonCount=TEST_SUMMON_COUNT,
        testSummonCost=TEST_SUMMON_COST,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({pet_bridge.petCount} pets, {pet_bridge.eggCount} eggs, "
        f"{pet_bridge.hatchSlotCount} hatch slots, "
        f"SummonButton x{TEST_SUMMON_COUNT}, cost {TEST_SUMMON_COST}, "
        f"dump={DUMP_PATH.name})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
