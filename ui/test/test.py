import sys
import time

from app.harness import UI_DIR

from _harness import create_app_engine, default_window_size, load_qml, set_window_context


def handle_qml_warnings(warnings):
	for warning in warnings:
		print(warning.toString())


def main() -> None:
	app, engine = create_app_engine()
	engine.warnings.connect(handle_qml_warnings)
	engine.addImportPath(str(UI_DIR))

	init_width, init_height = default_window_size(app, 0.48, 0.82)
	set_window_context(engine, init_width, init_height)

	load_start = time.perf_counter()
	ok = load_qml(engine, "test/test.qml")
	load_ms = (time.perf_counter() - load_start) * 1000
	print(f"QML loaded in {load_ms:.0f}ms (CurrencyView / SummonButton preview)")

	if not ok:
		sys.exit(-1)
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
