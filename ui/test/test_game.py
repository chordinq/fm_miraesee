import sys

import time



from _harness import create_app_engine, default_window_size, load_qml, set_window_context

from game_test_session import GameTestSessionBridge





def handle_qml_warnings(warnings):

    for warning in warnings:

        print(warning.toString())





def main() -> None:

    app, engine = create_app_engine()

    engine.warnings.connect(handle_qml_warnings)



    init_width, init_height = default_window_size(app)

    session = GameTestSessionBridge(parent=engine)



    set_window_context(

        engine,

        init_width,

        init_height,

        gameSession=session,

        gameTest=session.skillTest,

        gameEquipmentCollection=session.equipment,

        gamePetCollection=session.petCollection,

        gamePetEggTest=session.petEggTest,

        gamePetSummonTest=session.petSummonTest,

        gameMountCollection=session.mountCollection,

        gameMountSummonTest=session.mountSummonTest,

        gameTechTreeForge=session.techTreeForge,
        gameTechTreePower=session.techTreePower,
        gameTechTreeSkillsPetTech=session.techTreeSkillsPetTech,

    )



    load_start = time.perf_counter()

    ok = load_qml(engine, "test_game.qml")

    load_ms = (time.perf_counter() - load_start) * 1000

    print(

        f"QML loaded in {load_ms:.0f}ms "

        f"(skills={session.skillTest.skillCollection.skillCount}, "

        f"pets={session.petCollection.petCount}, "

        f"mounts={session.mountCollection.mountCount}, "

        f"paste dump and click LoadDump)"

    )



    if not ok:

        sys.exit(-1)

    sys.exit(app.exec())





if __name__ == "__main__":

    main()

