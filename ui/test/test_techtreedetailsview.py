import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from controllers.collections.tech_tree_collection_bridge import TechTreeCollectionBridge
from core.game_logic.enums import TechTreeType
from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def _node_state_tag(bridge) -> str:
    if bridge.maxLevel:
        return "max"
    if bridge.isUpgradeComplete:
        return "claim"
    if bridge.isUpgrading:
        return "skip"
    if bridge.otherResearchInProgress:
        return "blocked"
    if bridge.canStartUpgrade:
        return "upgrade"
    if bridge.requirementsMet:
        return "ready"
    return "locked"


def _build_node_options(nodes) -> list[dict[str, object]]:
    options: list[dict[str, object]] = []
    seen_ids: set[int] = set()

    def add(bridge, tag: str) -> None:
        node_id = int(bridge.nodeId)
        if node_id in seen_ids:
            return
        seen_ids.add(node_id)
        options.append(
            {
                "nodeId": node_id,
                "label": f"{bridge.nodeKey} L{int(bridge.level) + 1} [{tag}]",
            }
        )

    priority = (
        ("upgrading", lambda bridge: bridge.isUpgrading),
        ("claim", lambda bridge: bridge.isUpgradeComplete),
        ("upgrade", lambda bridge: bridge.canStartUpgrade and not bridge.maxLevel),
        ("blocked", lambda bridge: bridge.otherResearchInProgress),
        ("max", lambda bridge: bridge.maxLevel),
        ("ready", lambda bridge: bridge.requirementsMet and not bridge.maxLevel),
    )
    for tag, predicate in priority:
        for bridge in nodes:
            if predicate(bridge):
                add(bridge, tag)

    for bridge in nodes:
        add(bridge, _node_state_tag(bridge))

    return options


def _pick_default_node_id(options: list[dict[str, object]]) -> int:
    preferred_tags = ("upgrading", "claim", "upgrade", "max", "ready")
    for tag in preferred_tags:
        for option in options:
            if f"[{tag}]" in str(option["label"]):
                return int(option["nodeId"])
    if options:
        return int(options[0]["nodeId"])
    return 0


def create_test_session(parent):
    text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(text))
    logic = GameLogic(player)
    tree_model = TechTreeCollectionBridge(
        logic,
        tree_type=TechTreeType.Forge,
        parent=parent,
    )
    tree_model.reload(logic)
    nodes = tree_model.nodes
    node_options = _build_node_options(nodes)
    default_node_id = _pick_default_node_id(node_options)
    return tree_model, node_options, default_node_id


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.55, 0.65)
    tree_model, node_options, default_node_id = create_test_session(engine)

    set_window_context(
        engine,
        init_width,
        init_height,
        testTechTreeModel=tree_model,
        testNodeOptions=node_options,
        testDefaultNodeId=default_node_id,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test/test_techtreedetailsview.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(TechTreeDetailsView, Forge, node={default_node_id})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
