# ui/services/localization.py — entity + UI string lookup (en/ko/ja)
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from configs.config import (
    AUTO_ITEM_MAPPING,
    ITEM_MAPPING,
    MOUNT_MAPPING,
    PET_MAPPING,
    SKILL_MAPPING,
)
from core.enums import ItemAge, ItemType, Rarity
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.constants.equipment_slots import SLOT_LABELS
from ui.services.locale import Language, locale_service


def item_mapping_key(age: int | ItemAge, item_type: ItemType, idx: int) -> str:
    return f"{int(age)}_{int(item_type)}_{idx}"

_ROOT = Path(__file__).resolve().parents[2]
_ENTITY_NAMES_PATH = _ROOT / "configs/localization/entity_names_en_ko_ja.json"
_STRING_TABLES_PATH = _ROOT / "configs/localization/string_tables_en_ko_ja.json"

_UI_STRINGS: dict[str, dict[str, str]] = {
    "settings": {"en": "Settings", "ko": "설정", "ja": "設定"},
    "language": {"en": "Language", "ko": "언어", "ja": "言語"},
    "close": {"en": "Close", "ko": "닫기", "ja": "閉じる"},
    "ok": {"en": "OK", "ko": "확인", "ja": "確認"},
}

# Language picker labels — always shown in native script (not translated)
LANGUAGE_NATIVE_LABELS: dict[str, str] = {
    "en": "English",
    "ko": "한국어",
    "ja": "日本語",
}


@lru_cache(maxsize=1)
def _entity_names() -> dict:
    with _ENTITY_NAMES_PATH.open(encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _loc_by_id() -> dict[int, dict[str, str]]:
    with _STRING_TABLES_PATH.open(encoding="utf-8") as f:
        tables = json.load(f)
    index: dict[int, dict[str, str]] = {}
    for rows in tables.values():
        for row in rows:
            row_id = row.get("id")
            en = row.get("en")
            if row_id is None or not en:
                continue
            index[int(row_id)] = {
                "en": en,
                "ko": row.get("ko", en),
                "ja": row.get("ja", en),
            }
    return index


@lru_cache(maxsize=1)
def _ui_string_index() -> dict[str, dict[str, str]]:
    with _STRING_TABLES_PATH.open(encoding="utf-8") as f:
        tables = json.load(f)
    index: dict[str, dict[str, str]] = {}
    for rows in tables.values():
        for row in rows:
            en = row.get("en")
            if not en or en in index:
                continue
            index[en] = {
                "en": en,
                "ko": row.get("ko", en),
                "ja": row.get("ja", en),
            }
    return index


def _pick(row: dict[str, str] | None, lang: Language) -> str:
    if not row:
        return ""
    return str(row.get(lang.value) or row.get("en") or "")


def _row_for_key(group: str, key: str) -> dict[str, str] | None:
    data = _entity_names().get(group, {}).get(key)
    if not data:
        return None
    return {"en": data.get("en", ""), "ko": data.get("ko", ""), "ja": data.get("ja", "")}


def ui_text(key: str) -> str:
    row = _UI_STRINGS.get(key)
    if row:
        return _pick(row, locale_service.language)
    return key


def translate_id(loc_id: int) -> str:
    """Resolve localized text by string_tables entry id."""
    row = _loc_by_id().get(int(loc_id))
    if row:
        return _pick(row, locale_service.language)
    return str(loc_id)


def translate_en(en: str) -> str:
    """Resolve a Unity English key from string tables (UI labels)."""
    row = _ui_string_index().get(en)
    if row:
        return _pick(row, locale_service.language)
    return en


def item_display_name(item: ItemModel) -> str:
    key = item_mapping_key(item.age, item.item_type, item.idx)
    auto = AUTO_ITEM_MAPPING.get(key)
    en = None
    if auto and auto.get("ItemName"):
        en = str(auto["ItemName"])
    else:
        entry = ITEM_MAPPING.get(key)
        if entry:
            en = str(entry.get("Name", key))
    if en:
        row = _ui_string_index().get(en) or _row_for_key("items", key)
        if row:
            return _pick(row, locale_service.language)
        return en
    slot = SLOT_LABELS.get(item.item_type, "?")
    return f"{slot} #{item.idx}"


def age_display_name(age: int | ItemAge) -> str:
    row = _row_for_key("ages", str(int(age)))
    if row:
        return _pick(row, locale_service.language)
    try:
        return ItemAge(int(age)).name
    except (ValueError, KeyError):
        return str(age)


def pet_display_name(pet: PetModel) -> str:
    key = f"{int(pet.rarity)}_{int(pet.idx)}"
    row = _row_for_key("pets", key)
    if row:
        return _pick(row, locale_service.language)
    return f"Pet #{pet.idx}"


def mount_display_name(mount: MountModel) -> str:
    key = f"{int(mount.rarity)}_{int(mount.idx)}"
    row = _row_for_key("mounts", key)
    if row:
        return _pick(row, locale_service.language)
    return f"Mount #{mount.idx}"


def skill_display_name(skill: SkillModel) -> str:
    return skill_mapping_name(skill.rarity, skill.idx)


def pet_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    row = _row_for_key("pets", key)
    if row:
        return _pick(row, locale_service.language)
    entry = PET_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Pet#{idx}"


def mount_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    row = _row_for_key("mounts", key)
    if row:
        return _pick(row, locale_service.language)
    entry = MOUNT_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Mount#{idx}"


def skill_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    row = _row_for_key("skills", key)
    if row:
        return _pick(row, locale_service.language)
    entry = SKILL_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Skill#{idx}"
