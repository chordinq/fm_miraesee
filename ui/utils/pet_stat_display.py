from __future__ import annotations

from config import STATS_MAPPING
from core.game_logic.enums import SecondaryStatType
from core.game_logic.number_format import format_stat
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_pet_collection_model import PlayerPetModel
from core.game_logic.stats.pet_stats import resolve_pet_primary_stats

_DAMAGE_LABEL_LOC_ID = "988835206590464"
_HEALTH_LABEL_LOC_ID = "989213239209984"
_STATS_LOC_TABLE = "Stats"


def _secondary_label_loc(stat_type: SecondaryStatType) -> tuple[str, str]:
    entry = STATS_MAPPING["SecondaryStatType"][str(int(stat_type.value))]
    loc = entry["Localization"][0]
    return str(loc["Id"]), loc["File"]


def _format_secondary_value(stat_type: SecondaryStatType, value: float) -> str:
    if stat_type == SecondaryStatType.SkillCooldownMulti:
        pct = (value - 1.0) * 100.0
        text = f"{pct:+.1f}".rstrip("0").rstrip(".")
        return f"{text}%"
    pct = value * 100.0
    rounded = round(pct, 1)
    if abs(rounded - round(rounded)) < 0.05:
        return f"+{int(round(rounded))}%"
    return f"+{rounded:.1f}%"


def build_pet_stat_lines(
    player: PlayerModel,
    pet: PlayerPetModel,
) -> list[dict[str, object]]:
    game_config = player.game_config
    damage, health = resolve_pet_primary_stats(player, pet)
    lines: list[dict[str, object]] = [
        {
            "value": format_stat(damage),
            "labelLocId": _DAMAGE_LABEL_LOC_ID,
            "labelLocTable": _STATS_LOC_TABLE,
            "secondary": False,
        },
        {
            "value": format_stat(health),
            "labelLocId": _HEALTH_LABEL_LOC_ID,
            "labelLocTable": _STATS_LOC_TABLE,
            "secondary": False,
        },
    ]
    for stat_type in sorted(
        pet.secondary_stats.interpolated_stat_values.keys(),
        key=lambda entry: entry.value,
    ):
        found, resolved = pet.secondary_stats.try_get_stat_value(stat_type, game_config)
        if not found:
            continue
        label_loc_id, label_loc_table = _secondary_label_loc(stat_type)
        lines.append(
            {
                "value": _format_secondary_value(stat_type, resolved),
                "labelLocId": label_loc_id,
                "labelLocTable": label_loc_table,
                "secondary": True,
            }
        )
    return lines
