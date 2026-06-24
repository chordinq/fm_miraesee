"""Game config type schemas (MetaMember tag -> JSON field name)."""

from __future__ import annotations

from .meta_reader import map_fields, parse_object_table, parse_tagged_root
from .game_types import decode_item_id

DUNGEON_BASE_CONFIG = {
    1: "MaxDungeonLevel",
    2: "DailyDungeonKeys",
}

BASE_CONFIG = {
    1: "MaxAge",
    2: "EnemyHammerDropChance",
    3: "ForgeUnlockAfterForgesCount",
    100: "StartingGems",
    101: "StartingHammers",
    102: "ForgeLevelPushNoteTrigger",
    103: "SecondsToFullyRegenerate",
}


def decode_dungeon_base_config(blob: bytes) -> dict:
    fields = parse_tagged_root(blob)
    return map_fields(fields, DUNGEON_BASE_CONFIG)


def decode_base_config(blob: bytes) -> dict:
    fields = parse_tagged_root(blob)
    return map_fields(fields, BASE_CONFIG)


def decode_enemy_library(blob: bytes) -> dict[str, dict]:
    rows, _ = parse_object_table(blob)
    out: dict[str, dict] = {}
    for fields in rows:
        enemy_idx = fields[1]
        out[str(enemy_idx)] = {
            "EnemyIdx": enemy_idx,
            "WeaponId": decode_item_id(fields.get(2)),
            "HelmetId": decode_item_id(fields.get(3)),
            "ArmourId": decode_item_id(fields.get(4)),
        }
    return out


DECODERS: dict[str, object] = {
    "DungeonBaseConfig": decode_dungeon_base_config,
    "BaseConfig": decode_base_config,
    "EnemyLibrary": decode_enemy_library,
}
