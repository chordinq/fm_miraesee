import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from core.game_logic.enums import TechTreeType
from controllers.collections.tech_tree_collection_bridge import TechTreeCollectionBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def _bridge_summary(name: str, bridge: TechTreeCollectionBridge) -> str:
    return (
        f"{name} {bridge.nodeCount} nodes, "
        f"layers 0-{bridge.maxLayer}, "
        f"progress {bridge.progress * 100:.1f}%"
    )


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.95, 0.9)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))

    forge_bridge = TechTreeCollectionBridge(
        player,
        tree_type=TechTreeType.Forge,
        parent=engine,
    )
    power_bridge = TechTreeCollectionBridge(
        player,
        tree_type=TechTreeType.Power,
        parent=engine,
    )
    skills_pet_tech_bridge = TechTreeCollectionBridge(
        player,
        tree_type=TechTreeType.SkillsPetTech,
        parent=engine,
    )

    set_window_context(
        engine,
        init_width,
        init_height,
        testTechTreeForge=forge_bridge,
        testTechTreePower=power_bridge,
        testTechTreeSkillsPetTech=skills_pet_tech_bridge,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_tech.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(f"QML loaded in {load_ms:.0f}ms (dump={DUMP_PATH.name})")
    print(_bridge_summary("Forge", forge_bridge))
    print(_bridge_summary("Power", power_bridge))
    print(_bridge_summary("SkillsPetTech", skills_pet_tech_bridge))

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
