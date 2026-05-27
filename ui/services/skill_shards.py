# ui/services/skill_shards.py — shard progress label for skill tiles
from __future__ import annotations

from configs.config import SKILL_UPGRADE_LIBRARY
from core.game_logic.player_model.SkillModel import SkillModel


def next_level_shard_cost(skill: SkillModel) -> int | None:
    entry = SKILL_UPGRADE_LIBRARY.get(str(skill.level + 1))
    if not entry:
        return None
    return int(entry["Shards"])


def shard_progress_label(skill: SkillModel) -> str:
    cost = next_level_shard_cost(skill)
    if cost is None:
        return f"{skill.shard_count}/—"
    return f"{skill.shard_count}/{cost}"
