# cli/ui/hints.py — footer descriptions for focused UI items
from __future__ import annotations


def _lang() -> str:
    try:
        from cli.ui.screens.options import get_language
        return get_language()
    except Exception:
        return "en"


def _pick(en: str, ko: str) -> str:
    return ko if _lang() == "ko" else en


def main_menu_hint(focus: int) -> str:
    items = [
        _pick("Load a HEX dump and open the simulation hub.", "HEX 덤프를 불러와 시뮬레이션 허브를 엽니다."),
        _pick("Choose display language (English / Korean).", "표시 언어를 선택합니다 (English / 한국어)."),
        _pick("Version info and credits.", "버전 정보와 제작자 안내."),
        _pick("Exit the application.", "프로그램을 종료합니다."),
    ]
    return items[min(focus, len(items) - 1)]


def options_hint(focus: int) -> str:
    if focus == 0:
        return _pick("Use English names for skills, pets, and UI text.", "스킬·펫·UI 텍스트를 영어로 표시합니다.")
    return _pick("Use Korean names where available.", "가능한 항목은 한국어 이름으로 표시합니다.")


def about_hint() -> str:
    return _pick("ForgeMaster dump simulator — offline gear and summon lab.", "ForgeMaster 덤프 시뮬레이터 — 장비·소환 실험용.")


def hub_hint(tab_key: str, nav_key: str) -> str:
    tab_hints = {
        "profile": _pick("Inspect your dump: stats, gear, and collections.", "덤프 상태를 확인합니다: 스탯, 장비, 컬렉션."),
        "simulators": _pick("Run forge, summons, and hatches on dump state.", "덤프 기준으로 대장간·소환·부화를 실행합니다."),
        "calculators": _pick("Calculators — coming soon.", "계산기 — 준비 중."),
    }
    profile_nav = {
        "stats": _pick("Aggregated secondary stats from skills and equipment.", "스킬·장비에서 합산된 세컨더리 스탯."),
        "forge": _pick("Equipped items and forge level from the dump.", "덤프에 착용된 장비와 대장간 레벨."),
        "skill": _pick("Skill collection, summon level, and ticket progress.", "스킬 컬렉션·소환 레벨·티켓 진행도."),
        "pet": _pick("Pets, eggs in collection, and hatch slots.", "펫·알 컬렉션 및 부화 슬롯."),
        "mount": _pick("Mount collection and summon progress.", "탈것 컬렉션·소환 진행도."),
    }
    sim_nav = {
        "forge": _pick("Simulate forging with hammers on dump state.", "덤프 기준 망치 대장간 시뮬레이션."),
        "skill": _pick("Simulate skill summons (uses tickets & RNG seed).", "스킬 소환 시뮬레이션 (티켓·RNG 시드)."),
        "pet": _pick("Simulate egg summons and hatch predictions.", "알 소환·부화 예측 시뮬레이션."),
        "mount": _pick("Simulate mount summons.", "탈것 소환 시뮬레이션."),
        "soon": _pick("This section is not available yet.", "아직 사용할 수 없습니다."),
    }
    if tab_key == "simulators":
        return sim_nav.get(nav_key, tab_hints.get(tab_key, ""))
    if tab_key == "profile":
        return profile_nav.get(nav_key, tab_hints.get(tab_key, ""))
    return tab_hints.get(tab_key, _pick("Select a tab or item.", "탭 또는 항목을 선택하세요."))


def sim_action_hint(sim_kind: str, action_key: str) -> str:
    if action_key == "back":
        return _pick("Return to the simulator category list.", "시뮬레이터 목록으로 돌아갑니다.")
    if action_key == "hatch":
        return _pick("Predict hatch results for eggs in hatch slots.", "부화 슬롯 알의 부화 결과를 예측합니다.")
    if action_key == "hatch_all":
        return _pick("Predict hatch for every egg in hatch slots.", "부화 슬롯의 모든 알을 예측합니다.")
    if action_key.startswith("forge_"):
        n = action_key.split("_", 1)[1]
        return _pick(f"Forge {n} time(s) and show rolled gear.", f"대장간 {n}회 실행 후 장비 결과를 표시합니다.")
    if action_key.startswith("summon_"):
        n = action_key.rsplit("_", 1)[-1]
        kind = {"skill": "skill", "pet": "egg", "mount": "mount"}.get(sim_kind, "summon")
        return _pick(f"Summon {kind} ×{n} on dump RNG state.", f"덤프 RNG 기준 {kind} ×{n} 소환.")
    return _pick("Run the selected simulation.", "선택한 시뮬레이션을 실행합니다.")
