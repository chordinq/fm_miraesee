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
from core.enums import ItemAge, ItemType, Rarity, SecondaryStatType, StatType, SummonKind
from core.game_logic.player_model.ItemModel import ItemModel
from core.game_logic.player_model.MountModel import MountModel
from core.game_logic.player_model.PetModel import PetModel
from core.game_logic.player_model.SkillModel import SkillModel
from ui.theme.config.loc_ids import EGG_LABEL_LOC_ID, EQUIPPED_LABEL_LOC_ID
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
    "coming_soon": {"en": "Coming Soon!", "ko": "곧 출시!", "ja": "近日公開！"},
    "summon": {"en": "Summon", "ko": "소환", "ja": "召喚"},
    "summon_repeat": {"en": "Repeat", "ko": "반복", "ja": "繰り返し"},
    "summon_batch": {"en": "Per summon", "ko": "1회 소환", "ja": "1回召喚"},
    "summon_results": {"en": "Summon results", "ko": "소환 결과", "ja": "召喚結果"},
    "summon_new": {"en": "NEW", "ko": "신규", "ja": "NEW"},
    "summon_shard": {"en": "Shard", "ko": "조각", "ja": "欠片"},
    "summon_no_tickets": {
        "en": "Not enough skill summon tickets.",
        "ko": "스킬 소환권이 부족합니다.",
        "ja": "スキル召喚チケットが足りません。",
    },
    "summon_total": {"en": "Total pulls", "ko": "총 소환", "ja": "合計召喚"},
    "history": {"en": "History", "ko": "기록", "ja": "履歴"},
    "loading": {"en": "Loading dump…", "ko": "덤프 불러오는 중…", "ja": "ダンプ読み込み中…"},
    "clipboard_empty": {
        "en": "Clipboard is empty — copy the dump first.",
        "ko": "클립보드가 비어 있습니다 — 덤프를 먼저 복사하세요.",
        "ja": "クリップボードが空です — まずダンプをコピーしてください。",
    },
    "parse_failed": {
        "en": "Failed to parse dump.",
        "ko": "덤프 파싱에 실패했습니다.",
        "ja": "ダンプの解析に失敗しました。",
    },
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


def _row_for_key(group: str, key: str) -> dict | None:
    data = _entity_names().get(group, {}).get(key)
    if not data:
        return None
    return data


def _enum_row(enum_name: str, value: int) -> dict | None:
    return _entity_names().get("enums", {}).get(enum_name, {}).get(str(int(value)))


def _text_from_entry(entry: dict | None) -> str:
    if not entry:
        return ""
    inline = _pick(
        {"en": entry.get("en", ""), "ko": entry.get("ko", ""), "ja": entry.get("ja", "")},
        locale_service.language,
    )
    if inline:
        return inline
    loc_id = entry.get("id")
    if loc_id is not None:
        return translate_id(int(loc_id))
    return ""


def translate_enum(enum_name: str, value: int) -> str:
    """Localized label for a core.enums IntEnum member (via entity_names.enums)."""
    text = _text_from_entry(_enum_row(enum_name, value))
    return text or str(value)


def secondary_stat_display_name(stat_type: SecondaryStatType) -> str:
    """Localized SecondaryStatType label (entity_names.enums.SecondaryStatType)."""
    return translate_enum("SecondaryStatType", int(stat_type))


def stat_type_display_name(stat_type: StatType) -> str:
    """Localized StatType label (entity_names.enums.StatType — e.g. Damage, Health)."""
    return translate_enum("StatType", int(stat_type))


def summon_kind_display_name(kind: SummonKind) -> str:
    """Localized SummonKind label (entity_names.enums.SummonKind)."""
    return translate_enum("SummonKind", int(kind))


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


def translate_id_fmt(loc_id: int, *args: object) -> str:
    """Resolve localized text and substitute {0}, {1}, {2}... positional placeholders.

    Example:
        translate_id_fmt(996302057472, 50, 100, 10)
        → "영감을 받아 10초 동안 피해를 50 및 체력을 100 증가시킵니다"
    """
    template = translate_id(loc_id)
    if not args:
        return template
    try:
        return template.format(*args)
    except (IndexError, KeyError):
        return template


def translate_en(en: str) -> str:
    """Resolve a Unity English key from string tables (UI labels)."""
    row = _ui_string_index().get(en)
    if row:
        return _pick(row, locale_service.language)
    return en


def egg_label() -> str:
    return translate_id(EGG_LABEL_LOC_ID) or "Egg"


def equipped_label() -> str:
    return translate_id(EQUIPPED_LABEL_LOC_ID) or "Equipped"


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
    row = _row_for_key("items", key)
    if row:
        return _text_from_entry(row)
    if en:
        row = _ui_string_index().get(en)
        if row:
            return _pick(row, locale_service.language)
        return en
    return f"{item_type_display_name(item.item_type)} #{item.idx}"


def item_type_display_name(item_type: ItemType) -> str:
    return translate_enum("ItemType", int(item_type))


def age_display_name(age: int | ItemAge) -> str:
    return translate_enum("ItemAge", int(age))


def rarity_display_name(rarity: int | Rarity) -> str:
    return translate_enum("Rarity", int(rarity))


def combat_skill_display_name(combat_skill: int) -> str:
    return translate_enum("CombatSkill", int(combat_skill))


def pet_display_name(pet: PetModel) -> str:
    return pet_mapping_name(pet.rarity, pet.pet_id)


def mount_display_name(mount: MountModel) -> str:
    return mount_mapping_name(mount.rarity, mount.mount_id)


def skill_display_name(skill: SkillModel) -> str:
    return skill_mapping_name(skill.rarity, skill.idx)


def pet_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    text = _text_from_entry(_row_for_key("pets", key))
    if text:
        return text
    entry = PET_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Pet#{idx}"


def mount_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    text = _text_from_entry(_row_for_key("mounts", key))
    if text:
        return text
    entry = MOUNT_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Mount#{idx}"


def skill_mapping_name(rarity: int | Rarity, idx: int) -> str:
    key = f"{int(rarity)}_{int(idx)}"
    text = _text_from_entry(_row_for_key("skills", key))
    if text:
        return text
    entry = SKILL_MAPPING.get(key)
    return str(entry["Name"]) if entry else f"Skill#{idx}"
