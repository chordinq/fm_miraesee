import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from controllers.collections.mount_collection_bridge import MountCollectionBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    mount_bridge = MountCollectionBridge(
        player.player_mount_collection_model,
        player,
        parent=engine,
    )

    set_window_context(
        engine,
        init_width,
        init_height,
        testMountCollection=mount_bridge,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_mount.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({mount_bridge.mountCount} mounts from {DUMP_PATH.name})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
