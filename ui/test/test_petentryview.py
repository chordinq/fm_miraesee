import sys
import time

from _harness import create_app_engine, default_window_size, load_qml, set_window_context
from config import PETS_MAPPING
from core.game_logic.enums import Rarity
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PetId, create_pet
from core.game_logic.config.shared_game_config import get_shared_game_config
from core.random_pcg import RandomPCG
from controllers.models.pet_model_bridge import PetModelBridge

TEST_PET_KEY = "Griffin"
TEST_PET_LEVEL = 43


def create_test_pet_model(parent) -> PetModelBridge:
    player = PlayerModel(game_config=get_shared_game_config())
    collection = player.player_pet_collection_model
    key_by_name = {entry["Key"]: map_key for map_key, entry in PETS_MAPPING.items()}

    map_key = key_by_name.get(TEST_PET_KEY)
    if map_key is None:
        raise RuntimeError(f"Pet key not found: {TEST_PET_KEY}")

    data = PETS_MAPPING[map_key]
    pet_id = PetId(Rarity(data["Rarity"]), data["Idx"])
    rng = RandomPCG.create_from_seed(0)
    pet = create_pet(player, pet_id, rng)
    pet.level = TEST_PET_LEVEL

    collection.pets.append(pet)
    player.player_power_model.update_power(player, True)
    return PetModelBridge(pet, player, parent=parent)


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.72, 0.42)
    pet_model = create_test_pet_model(engine)

    set_window_context(
        engine,
        init_width,
        init_height,
        testPetModel=pet_model,
        testAscensionLevels=[0, 1, 2, 3],
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_petentryview.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(PetEntryView ascension 0-3, {TEST_PET_KEY} L{TEST_PET_LEVEL + 1})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
