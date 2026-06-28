from __future__ import annotations

from config import GUILD_WAR_DAY_CONFIG_LIBRARY
from core.game_logic.actions.summon.skill_summon_action import SummonedSkillInfo
from core.game_logic.enums import Rarity, WarTask
from core.game_logic.player.player_skill_collection_model import combat_skill_to_skill_id


def _war_points_by_task(day: int) -> dict[str, int]:
    day_config = GUILD_WAR_DAY_CONFIG_LIBRARY.get(str(day))
    if day_config is None:
        return {}

    lookup: dict[str, int] = {}
    for task_entry in day_config.get("Tasks", []):
        task_name = task_entry.get("Task")
        if not task_name:
            continue
        for reward in task_entry.get("Rewards", []):
            if reward.get("$type") == "WarPointsReward":
                lookup[task_name] = int(reward.get("Amount", 0))
                break
    return lookup


def war_points_for_skill_summon_rarity(day: int, rarity: Rarity) -> int:
    task = WarTask(3000 + rarity.value)
    return _war_points_by_task(day).get(task.name, 0)


def war_points_for_skill_summon(day: int, summoned: list[SummonedSkillInfo]) -> int:
    total = 0
    for info in summoned:
        skill_id = combat_skill_to_skill_id(info.type)
        total += war_points_for_skill_summon_rarity(day, skill_id.rarity)
    return total


def war_points_for_skill_upgrade_rarity(day: int, rarity: Rarity) -> int:
    task = WarTask(4006 + rarity.value)
    return _war_points_by_task(day).get(task.name, 0)


def war_points_for_skill_upgrades(day: int, upgraded_skills: list) -> int:
    total = 0
    for skill in upgraded_skills:
        skill_id = combat_skill_to_skill_id(skill.type)
        total += war_points_for_skill_upgrade_rarity(day, skill_id.rarity)
    return total
