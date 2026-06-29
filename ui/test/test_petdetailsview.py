import sys
import time

from _harness import create_app_engine, default_window_size, load_qml, set_window_context
from config import PETS_MAPPING
from core.game_logic.enums import Rarity
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PetId, create_pet
from core.game_logic.shared_game_config import get_shared_game_config
from core.random_pcg import RandomPCG
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.summon.pet_summon_test_bridge import PetSummonTestBridge

TEST_PET_KEY = "Cerberus"
TEST_PET_LEVEL = 43
TEST_PET_SEED = 0xC0FFEE


def create_test_session(parent):
    player = PlayerModel(game_config=get_shared_game_config())
    collection = player.player_pet_collection_model
    key_by_name = {entry["Key"]: map_key for map_key, entry in PETS_MAPPING.items()}

    map_key = key_by_name.get(TEST_PET_KEY)
    if map_key is None:
        raise RuntimeError(f"Pet key not found: {TEST_PET_KEY}")

    data = PETS_MAPPING[map_key]
    pet_id = PetId(Rarity(data["Rarity"]), data["Idx"])
    pet = create_pet(player, pet_id, RandomPCG.create_from_seed(TEST_PET_SEED))
    pet.level = TEST_PET_LEVEL

    collection.pets.append(pet)
    player.player_power_model.update_power(player, True)

    pet_collection = PetCollectionBridge(collection, player, parent=parent)
    pet_controller = PetSummonTestBridge(GameLogic(player), pet_collection, parent=parent)
    return pet_collection.pets[0], pet_controller


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.55, 0.65)
    pet_model, pet_controller = create_test_session(engine)

    set_window_context(
        engine,
        init_width,
        init_height,
        testPetModel=pet_model,
        testPetController=pet_controller,
        testAscensionLevels=[0, 1, 2, 3],
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_petdetailsview.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(PetDetailsView, {TEST_PET_KEY} L{TEST_PET_LEVEL + 1})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
