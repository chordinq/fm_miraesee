import sys
import time

from _harness import create_app_engine, default_window_size, load_qml, set_window_context

TEST_SUMMON_COUNT = 5
TEST_SUMMON_COST = 176


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.6, 0.75)
    set_window_context(
        engine,
        init_width,
        init_height,
        testSummonCount=TEST_SUMMON_COUNT,
        testSummonCost=TEST_SUMMON_COST,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(SummonButton x{TEST_SUMMON_COUNT}, cost {TEST_SUMMON_COST})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
