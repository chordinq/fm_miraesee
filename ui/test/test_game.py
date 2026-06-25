import sys
import time

from _harness import DUMP_PATH, create_app_engine, default_window_size, load_qml, set_window_context
from core.game_logic.enums import TechTreeType
from core.game_logic.game_logic import GameLogic
from equipment_collection_bridge import EquipmentCollectionBridge
from mount_collection_bridge import MountCollectionBridge
from pet_collection_bridge import PetCollectionBridge
from pet_egg_test_bridge import PetEggTestBridge
from skill_summon_test_bridge import SkillSummonTestBridge
from tech_tree_collection_bridge import TechTreeCollectionBridge
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
    logic = GameLogic(player)

    game_test = SkillSummonTestBridge(logic, parent=engine)
    equipment_bridge = EquipmentCollectionBridge(
        player.player_equipment_model,
        parent=engine,
    )
    pet_bridge = PetCollectionBridge(
        player.player_pet_collection_model,
        player,
        parent=engine,
    )
    pet_egg_test = PetEggTestBridge(logic, pet_bridge, parent=engine)
    mount_bridge = MountCollectionBridge(
        player.player_mount_collection_model,
        parent=engine,
    )
    tech_bridge = TechTreeCollectionBridge(
        player,
        tree_type=TechTreeType.Forge,
        parent=engine,
    )

    set_window_context(
        engine,
        init_width,
        init_height,
        gameTest=game_test,
        gameEquipmentCollection=equipment_bridge,
        gamePetCollection=pet_bridge,
        gamePetEggTest=pet_egg_test,
        gameMountCollection=mount_bridge,
        gameTechTree=tech_bridge,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_game.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(skills={game_test.skillCollection.skillCount}, "
        f"pets={pet_bridge.petCount}, mounts={mount_bridge.mountCount}, "
        f"dump={DUMP_PATH.name})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
