import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from skill_summon_test_bridge import SkillSummonTestBridge
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model
from core.game_logic.game_logic import GameLogic


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app)
    dump_text = DUMP_PATH.read_text(encoding="utf-8")
    player = dump_snapshot_to_player_model(parse_dump_text(dump_text))
    game_test = SkillSummonTestBridge(GameLogic(player), parent=engine)

    set_window_context(engine, init_width, init_height, gameTest=game_test)

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_game.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({game_test.skillCollection.skillCount} skills, dump={DUMP_PATH.name})"
    )
    print(game_test.predictionText)

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
