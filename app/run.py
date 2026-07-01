from __future__ import annotations

import sys
import time

from app.harness import (
	create_application,
	create_qml_engine,
	default_window_size,
	load_qml,
	register_qml_services,
	set_window_context,
	show_loading_screen,
)


def handle_qml_warnings(warnings) -> None:
	for warning in warnings:
		print(warning.toString())


def main() -> None:
	app = create_application()
	engine = create_qml_engine()
	engine.warnings.connect(handle_qml_warnings)

	init_width, init_height = default_window_size(app)
	if not show_loading_screen(app, engine):
		sys.exit(-1)

	register_qml_services(engine)

	from app.session import GameTestSessionBridge

	session = GameTestSessionBridge(parent=engine)

	set_window_context(
		engine,
		init_width,
		init_height,
		app,
        gameSession=session,
        gamePlayerStats=session.playerStats,
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
	ok = load_qml(engine, "main_window.qml", app, replace=True)
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
