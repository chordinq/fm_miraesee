from __future__ import annotations

from config import STATS_MAPPING
from core.game_logic.enums import SecondaryStatType
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_mount_collection_model import PlayerMountModel

def _label_loc_segments(localizations: list[dict]) -> list[dict[str, str]]:
    return [
        {"locId": str(loc["Id"]), "locTable": loc["File"]}
        for loc in localizations
    ]


def _secondary_label_segments(stat_type: SecondaryStatType) -> list[dict[str, str]]:
    entry = STATS_MAPPING["SecondaryStatType"][str(int(stat_type.value))]
    return _label_loc_segments(entry["Localization"])


def build_mount_stat_lines(
    player: PlayerModel,
    mount: PlayerMountModel,
) -> list[dict[str, object]]:
    game_config = player.game_config
    lines: list[dict[str, object]] = []
    for stat_type in mount.secondary_stats.interpolated_stat_values.keys():
        found, resolved = mount.secondary_stats.try_get_stat_value(stat_type, game_config)
        if not found:
            continue
        lines.append(
            {
                "rawValue": resolved,
                "secondaryStatType": int(stat_type.value),
                "labelLocSegments": _secondary_label_segments(stat_type),
                "secondary": True,
            }
        )
    return lines
