"""One-shot forge smoke test from test_user_dump.txt."""
from pathlib import Path

from core.game_logic.enums import CurrencyType
from core.game_logic.game_logic import GameLogic
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model

player = dump_snapshot_to_player_model(
	parse_dump_text(Path("test_user_dump.txt").read_text(encoding="utf-8"))
)
logic = GameLogic(player)
forge = player.player_forge_model
hammers = player.player_currency_model.get(CurrencyType.Hammers)
print(
	f"forge_level={forge.forge_level} seed={forge.forge_seed:#x} "
	f"hammers={hammers} pending={len(forge.pending_items)}"
)
result, items = logic.forge(1, commit=True)
print(
	f"result={result.name} forged={len(items)} "
	f"pending={len(forge.pending_items)} seed_after={forge.forge_seed:#x}"
)
for it in items:
	print(
		f"  item age={it.item_id.Age.name} type={it.item_id.Type.name} "
		f"idx={it.item_id.Idx} level={it.level}"
	)
