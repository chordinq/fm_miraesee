"""
Parse GameGuardian / miraesee_data_exporter.lua text dumps into PlayerModel.

Implementation lives in utils.dump; this module keeps the legacy import path.
"""

from __future__ import annotations

from utils.dump import DumpTextParser, dump_snapshot_to_player_model, parse_dump, parse_dump_text
from utils.dump.snapshot import DumpSnapshot

__all__ = [
	"DumpParser",
	"DumpSnapshot",
	"parse_dump",
]


class DumpParser:
	"""Legacy alias — parses text → PlayerModel via DumpSnapshot."""

	def parse(self, text: str):
		return parse_dump(text)
