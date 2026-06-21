import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from core.game_logic.enums import AscensionLevel
from egg_model_bridge import EggModelBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def _equipped_egg_bridges(player) -> list[EggModelBridge]:
    collection = player.player_pet_collection_model
    ascension_level = AscensionLevel(collection.ascension_model.current_level)
    equipped = sorted(
        (egg for egg in collection.eggs if egg.is_equipped),
        key=lambda egg: egg.equip_slot,
    )
    return [
        EggModelBridge(egg, ascension_level=ascension_level)
        for egg in equipped
    ]


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.7, 0.5)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    hatch_eggs = _equipped_egg_bridges(player)

    set_window_context(
        engine,
        init_width,
        init_height,
        hatchEggModels=hatch_eggs,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_hatchslot.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({len(hatch_eggs)} equipped eggs, dump={DUMP_PATH.name})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
