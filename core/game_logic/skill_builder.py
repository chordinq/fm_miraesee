from __future__ import annotations

from .enums import CombatSkill

_DAMAGE_COUNT_TABLE_MASK = 0x20F

_DAMAGE_COUNT_BY_INDEX: dict[int, int] = {
	0: 3,
	1: 5,
	2: 8,
	3: 5,
	9: 5,
}


def get_skill_damage_count(combat_skill: CombatSkill) -> int:
	"""IL: SkillBuilder.GetSkillDamageCount(CombatSkill)

	Table indices use (int(combat_skill) - 2) when (0x20f >> index) & 1.
	Values from IL DAT_01b223f0 (Ghidra rodata dump).
	"""
	skill_value = int(combat_skill)
	index = skill_value - 2
	if 0 <= index < 10 and (_DAMAGE_COUNT_TABLE_MASK >> index) & 1:
		try:
			return _DAMAGE_COUNT_BY_INDEX[index]
		except KeyError as exc:
			raise NotImplementedError(
				f"SkillBuilder.GetSkillDamageCount table entry for index {index} "
				f"(CombatSkill.{combat_skill.name})"
			) from exc
	if skill_value == 0x10:
		return 3
	return 1
