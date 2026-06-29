import sys
import time

from _harness import create_app_engine, default_window_size, load_qml, set_window_context
from config import SKILL_UPGRADE_LIBRARY, SKILLS_MAPPING
from core.game_logic.enums import CombatSkill
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillModel
from core.game_logic.shared_game_config import get_shared_game_config
from controllers.models.skill_model_bridge import SkillModelBridge

TEST_SKILL_KEY = "Shout"
TEST_SKILL_LEVEL = 99


def _shards_required_for_next_level(level: int) -> int:
    entry = SKILL_UPGRADE_LIBRARY.get(str(level + 1))
    if entry is None:
        return 0
    return int(entry["Shards"])


def create_test_skill_model(parent) -> SkillModelBridge:
    player = PlayerModel(game_config=get_shared_game_config())
    collection = player.player_skill_collection_model
    key_by_name = {entry["Key"]: map_key for map_key, entry in SKILLS_MAPPING.items()}

    map_key = key_by_name.get(TEST_SKILL_KEY)
    if map_key is None:
        raise RuntimeError(f"Skill key not found: {TEST_SKILL_KEY}")

    data = SKILLS_MAPPING[map_key]
    combat_skill = CombatSkill(data["Type"])
    skill = PlayerSkillModel(combat_skill)
    skill.level = TEST_SKILL_LEVEL

    required = _shards_required_for_next_level(skill.level)
    if required > 0:
        skill.shard_count = required + 3

    collection.player_skills[combat_skill] = skill
    player.player_power_model.update_power(player, True)
    return SkillModelBridge(skill, player, parent=parent)


def handle_qml_warnings(warnings):
    for warning in warnings:
        print(warning.toString())


def main() -> None:
    app, engine = create_app_engine()
    engine.warnings.connect(handle_qml_warnings)

    init_width, init_height = default_window_size(app, 0.72, 0.42)
    skill_model = create_test_skill_model(engine)

    set_window_context(
        engine,
        init_width,
        init_height,
        testSkillModel=skill_model,
        testAscensionLevels=[0, 1, 2, 3],
    )

    load_start = time.perf_counter()
    ok = load_qml(engine, "test_skillentryview.qml")
    load_ms = (time.perf_counter() - load_start) * 1000
    print(
        f"QML loaded in {load_ms:.0f}ms "
        f"(SkillEntryView ascension 0-3, {TEST_SKILL_KEY} L{TEST_SKILL_LEVEL + 1})"
    )

    if not ok:
        sys.exit(-1)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
