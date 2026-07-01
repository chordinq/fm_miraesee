import sys
import time

from app.harness import TEST_LANGUAGE, UI_DIR
from core.game_logic.enums import CurrencyType
from ui.TMPText import inline_sprites
from ui.TMPText.tmp_text_bridge import TmpTextBridge

from _harness import create_app_engine, default_window_size, load_qml, set_window_context


def handle_qml_warnings(warnings):
	for warning in warnings:
		print(warning.toString())


def _register_tmp_text_samples(engine, bridge: TmpTextBridge) -> None:
	ctx = engine.rootContext()
	ctx.setContextProperty("TmpTextBridge", bridge)
	ctx.setContextProperty("sampleLevelPlusOne", bridge.format_level_plus_one_text(41, TEST_LANGUAGE, 1))
	ctx.setContextProperty("sampleLevelFull", bridge.format_level_text(99, TEST_LANGUAGE, 0))
	ctx.setContextProperty("sampleLongA", bridge.format_long_text(1342343))
	ctx.setContextProperty("sampleLongB", bridge.format_long_text(999))
	ctx.setContextProperty("sampleLongC", bridge.format_long_text(1500000000))
	ctx.setContextProperty("sampleStat", bridge.format_stat_text(1342343, 0))
	ctx.setContextProperty("samplePct", bridge.format_percentage_text(0.125))
	power_icon, power_text = inline_sprites.format_power_line(987654321)
	ctx.setContextProperty("samplePowerText", power_text)
	ctx.setContextProperty("samplePowerIcon", power_icon)

	currency_rows = [
		("Coins", CurrencyType.Coins, 1342343),
		("Gems", CurrencyType.Gems, 250),
		("Hammers", CurrencyType.Hammers, 12),
		("Skill tickets", CurrencyType.SkillSummonTickets, 1500),
		("Tech potions", CurrencyType.TechPotions, 88),
		("Eggshells", CurrencyType.Eggshells, 42000),
	]
	ctx.setContextProperty(
		"currencySamples",
		[
			{
				"label": label,
				"text": inline_sprites.format_currency_value_text(amount, currency_type),
				"iconSource": inline_sprites.currency_icon_source(currency_type),
			}
			for label, currency_type, amount in currency_rows
		],
	)


def main() -> None:
	app, engine = create_app_engine()
	engine.warnings.connect(handle_qml_warnings)
	engine.addImportPath(str(UI_DIR))

	bridge = TmpTextBridge()
	init_width, init_height = default_window_size(app, 0.48, 0.82)
	_register_tmp_text_samples(engine, bridge)
	set_window_context(engine, init_width, init_height)

	load_start = time.perf_counter()
	ok = load_qml(engine, "test/test.qml")
	load_ms = (time.perf_counter() - load_start) * 1000
	print(f"QML loaded in {load_ms:.0f}ms (TMPText / core.format preview)")

	if not ok:
		sys.exit(-1)
	sys.exit(app.exec())


if __name__ == "__main__":
	main()
