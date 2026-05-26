# cli/ui/screens/run_hub.py
from __future__ import annotations

from cli.core.frame import body_height
from cli.core.input import read_key
from cli.core.presenter import show_frame
from cli.core.terminal import drain_stdin
from cli.ui.components.hub import HEADER_ROWS, _NAV, _TABS, build_hub_frame
from cli.ui.hints import sim_action_hint

_PROFILE = {
    "stats": "cli.render.profile.stats",
    "forge": "cli.render.profile.forge",
    "skill": "cli.render.profile.skill",
    "pet": "cli.render.profile.pet",
    "mount": "cli.render.profile.mount",
}

_FORGE_COUNTS = [1, 10, 50, 100]


def _counts(kind: str) -> list[int]:
    from configs import SKILL_SUMMON_CONFIG, EGG_SUMMON_CONFIG, MOUNT_SUMMON_CONFIG
    m = {"skill": SKILL_SUMMON_CONFIG, "egg": EGG_SUMMON_CONFIG, "mount": MOUNT_SUMMON_CONFIG}
    return list(m[kind].possible_summon_count)


def _load_profile(key: str, session) -> list[str]:
    import importlib
    mod_path = _PROFILE.get(key)
    if not mod_path:
        return ["  (empty)"]
    mod = importlib.import_module(mod_path)
    return mod.render(session)


def _sim_menu(kind: str) -> list[tuple[str, str]]:
    if kind == "forge":
        return [(f"forge_{n}", f"Forge  ×{n}") for n in _FORGE_COUNTS]
    if kind == "skill":
        return [(f"summon_{n}", f"Summon  ×{n}") for n in _counts("skill")]
    if kind == "pet":
        items = [(f"summon_{n}", f"Egg summon  ×{n}") for n in _counts("egg")]
        return items + [("hatch", "Hatch slots"), ("hatch_all", "Hatch all")]
    if kind == "mount":
        return [(f"summon_{n}", f"Summon  ×{n}") for n in _counts("mount")]
    return []


def _run_action(session, action: str, sim_kind: str, count: int) -> list[str]:
    if action.startswith("forge_"):
        from cli.services.forge import run_forge
        from cli.render.summon import forge as fr
        n = int(action.split("_", 1)[1])
        return fr.render(run_forge(session, n), n)
    if action.startswith("summon_"):
        from cli.services.summon import run_summon
        kind = {"skill": "skill", "pet": "egg", "mount": "mount"}[sim_kind]
        out = run_summon(session, kind, count)
        if not out.success:
            from cli.theme import err
            return [f"  {err(out.error)}"]
        if kind == "skill":
            from cli.render.summon import skill as r
            return r.render(out.pulls, count)
        if kind == "egg":
            from cli.render.summon import egg as r
            return r.render(out.pulls, count)
        from cli.render.summon import mount as r
        return r.render(out.pulls, count)
    if action in ("hatch", "hatch_all"):
        from cli.services.hatch import predict_all
        from cli.render.hatch_result import render as render_hatch
        target = "all" if action == "hatch_all" else ""
        return render_hatch(predict_all(session, target))
    return []


def _placeholder() -> list[str]:
    from cli.theme import C_MUTED, RESET
    return [f"  {C_MUTED}Select item · Enter to run{RESET}"]


def _tab_content(session, tab_key: str, nav: int) -> list[str]:
    items = _NAV.get(tab_key, [])
    if not items:
        return _placeholder()
    key = items[nav][0]
    if key == "soon":
        from cli.theme import C_MUTED, RESET
        return [f"  {C_MUTED}Coming soon{RESET}"]
    if tab_key in ("profile", "simulators"):
        return _load_profile(key, session)
    return _placeholder()


def run(session) -> None:
    tab, nav, scroll = 0, 0, 0
    content = _tab_content(session, _TABS[tab][0], nav)
    drain_stdin()

    while True:
        show_frame(
            build_hub_frame(
                session,
                tab_idx=tab,
                nav_idx=nav,
                content_lines=content,
                scroll=scroll,
            )
        )

        kind, code = read_key()
        if kind == "esc":
            return
        if kind == "enter":
            tab_key = _TABS[tab][0]
            items = _NAV.get(tab_key, [])
            if not items:
                continue
            item_key = items[nav][0]
            if tab_key == "profile":
                content = _tab_content(session, tab_key, nav)
                scroll = 0
            elif tab_key == "simulators":
                content = _sim_submenu(session, item_key, tab, nav)
                scroll = 0
            else:
                from cli.theme import C_MUTED, RESET
                content = [f"  {C_MUTED}Coming soon{RESET}"]
            continue

        if kind != "arrow":
            continue

        tab_key = _TABS[tab][0]
        if code == "left":
            tab = (tab - 1) % len(_TABS)
            nav, scroll = 0, 0
            content = _tab_content(session, _TABS[tab][0], nav)
        elif code == "right":
            tab = (tab + 1) % len(_TABS)
            nav, scroll = 0, 0
            content = _tab_content(session, _TABS[tab][0], nav)
        elif code == "up":
            items = _NAV.get(tab_key, [])
            nav = (nav - 1) % max(1, len(items))
            scroll = 0
            content = _tab_content(session, tab_key, nav)
        elif code == "down":
            items = _NAV.get(tab_key, [])
            nav = (nav + 1) % max(1, len(items))
            scroll = 0
            content = _tab_content(session, tab_key, nav)
        elif code == "pgup":
            scroll = max(0, scroll - 8)
        elif code == "pgdn":
            body = body_height(header_rows=HEADER_ROWS)
            scroll = min(max(0, len(content) - body), scroll + 8)


def _sim_submenu(session, sim_kind: str, tab: int, nav: int) -> list[str]:
    from cli.theme import C_SKY, C_WHITE, BOLD, RESET, C_MUTED

    actions = _sim_menu(sim_kind) + [("back", "← back")]
    focus = 0
    while True:
        sub = [f"  {C_SKY if i == focus else C_WHITE}{'▶ ' if i == focus else '  '}{lb}{RESET}"
               for i, (_, lb) in enumerate(actions)]
        action_key, _ = actions[focus]
        show_frame(
            build_hub_frame(
                session,
                tab_idx=tab,
                nav_idx=nav,
                content_lines=sub,
                scroll=0,
                footer=sim_action_hint(sim_kind, action_key),
            )
        )
        kind, code = read_key()
        if kind == "esc":
            return _placeholder()
        if kind == "arrow" and code == "up":
            focus = (focus - 1) % len(actions)
        elif kind == "arrow" and code == "down":
            focus = (focus + 1) % len(actions)
        elif kind == "enter":
            key, _ = actions[focus]
            if key == "back":
                return _tab_content(session, "simulators", nav)
            if key in ("hatch", "hatch_all"):
                return _run_action(session, key, sim_kind, 0)
            if key.startswith(("summon_", "forge_")):
                count = int(key.rsplit("_", 1)[-1])
            else:
                count = 0
            result = _run_action(session, key, sim_kind, count)
            if key.startswith("summon_"):
                return result + ["", f"  {C_MUTED}←→ tab or ↑↓ nav to view updated collection{RESET}"]
            return result
