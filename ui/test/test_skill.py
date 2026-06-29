import sys
import time

from _harness import create_app_engine, default_window_size, load_qml, set_window_context
from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from core.game_logic.enums import CombatSkill
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.shared_game_config import get_shared_game_config
from controllers.collections.skill_collection_bridge import SkillCollectionBridge

SKILL_TEST_KEYS = [
    "Meat",
    "Arrows",
    "Shout",
    "Shuriken",
    "Berserk",
    "CannonBarrage",
    "Thorns",
    "Buff",
    "RainOfArrows",
    "Morale",
    "Meteorite",
    "Bomb",
]

SKILL_TEST_LEVELS = [38, 42, 41, 53, 49, 51, 14, 13, 10, 3, 1, 5]

EQUIPPED_SKILL_KEY = "Buff"


def _shards_required_for_next_level(level: int) -> int:
    entry = SKILL_UPGRADE_LIBRARY.get(str(level + 1))
    if entry is None:
        return 0
    return int(entry["Shards"])


def create_skill_ui_test_player() -> PlayerModel:
    player = PlayerModel(game_config=get_shared_game_config())
    collection = player.player_skill_collection_model
    key_by_name = {entry["Key"]: map_key for map_key, entry in SKILLS_MAPPING.items()}

    for index, skill_key in enumerate(SKILL_TEST_KEYS):
        map_key = key_by_name.get(skill_key)
        if map_key is None:
            continue

        data = SKILLS_MAPPING[map_key]
        combat_skill = CombatSkill(data["Type"])
        skill = PlayerSkillModel(combat_skill)
        skill.level = SKILL_TEST_LEVELS[index] if index < len(SKILL_TEST_LEVELS) else 20

        required = _shards_required_for_next_level(skill.level)
        if required > 0:
            overflow = 3 if index % 4 == 0 else 0
            skill.shard_count = required + overflow

        if skill_key == EQUIPPED_SKILL_KEY:
            skill.is_equipped = True
            skill.equip_slot = 0

        collection.player_skills[combat_skill] = skill

    player.player_power_model.update_power(player, True)
    return player


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app)
    player = create_skill_ui_test_player()
    skill_collection_bridge = SkillCollectionBridge(
        player.player_skill_collection_model,
        player,
        parent=engine,
    )

    set_window_context(
        engine,
        init_width,
        init_height,
        testSkillCollection=skill_collection_bridge,
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_skill.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    upgradable_count = sum(
        1
        for skill in skill_collection_bridge.skills
        if skill.maxShardCount > 0 and skill.shardCount >= skill.maxShardCount
    )
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"({skill_collection_bridge.skillCount} synthetic skills, "
        f"{upgradable_count} upgradable)"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
