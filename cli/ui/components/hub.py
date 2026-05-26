# cli/ui/components/hub.py — Run hub frame builder (returns lines only)
from __future__ import annotations

from cli.core.ansi import pad_vis, visual_len
from cli.core.frame import FOOTER_ROWS, body_height, clip_pane, footer_line
from cli.ui.hints import hub_hint, sim_action_hint
from cli.core.terminal import term_width
from cli.theme import BOLD, C_MUTED, C_SKY, C_WHITE, RESET, dim, rgb

LEFT_W = 16
HEADER_ROWS = 5

_TABS = [("profile", "Profile"), ("simulators", "Simulators"), ("calculators", "Calculators")]
_NAV = {
    "profile": [("stats", "Stats"), ("forge", "Forge"), ("skill", "Skill"), ("pet", "Pet/Egg"), ("mount", "Mount")],
    "simulators": [("forge", "Forge"), ("skill", "Skill"), ("pet", "Pet/Egg"), ("mount", "Mount")],
    "calculators": [("soon", "Coming soon")],
}

_PURPLE = rgb(160, 80, 255)
_GREY = rgb(140, 140, 140)


def _currency(session) -> str:
    from constants.colors import CURRENCY_COLORS
    from core.enums import CurrencyType
    parts = []
    for label, ct in [
        ("Gems", CurrencyType.Gems), ("Coins", CurrencyType.Coins),
        ("Hammers", CurrencyType.Hammers), ("Tickets", CurrencyType.SkillSummonTickets),
        ("Eggshells", CurrencyType.Eggshells), ("Winders", CurrencyType.ClockWinders),
    ]:
        amt = session.player.currency.get_currency(ct)
        col = CURRENCY_COLORS.get(ct.name, "")
        parts.append(f"{col}{label}{RESET} {C_WHITE}{amt:,}{RESET}")
    return "  ·  ".join(parts)


def _top_bar(session, width: int) -> str:
    """MIRAESEE (left) · currencies (center) · v1.0.0 (right)."""
    lt = f"{_PURPLE}{BOLD}MIRAESEE{RESET}"
    rt = f"{_GREY}v1.0.0{RESET}"
    mid = _currency(session)
    lw, rw, mw = visual_len(lt), visual_len(rt), visual_len(mid)
    gap = width - lw - rw
    if gap <= 0:
        return pad_vis(lt + rt, width)
    if mw >= gap:
        return lt + pad_vis(mid, gap) + rt
    pad_l = (gap - mw) // 2
    pad_r = gap - mw - pad_l
    return lt + (" " * pad_l) + mid + (" " * pad_r) + rt


def build_hub_frame(
    session,
    *,
    tab_idx: int,
    nav_idx: int,
    content_lines: list[str],
    scroll: int = 0,
    footer: str | None = None,
) -> list[str]:
    W = term_width()
    body_h = body_height(header_rows=HEADER_ROWS)
    pane_w = max(1, W - LEFT_W - 3)

    tab_key = _TABS[tab_idx][0]
    nav_items = _NAV.get(tab_key, [])

    lines: list[str] = []
    lines.append(_top_bar(session, W))
    lines.append(dim("─" * W))

    tab_row = "  "
    for i, (_, lb) in enumerate(_TABS):
        tab_row += (f"{C_SKY}{BOLD}{lb}{RESET}" if i == tab_idx else f"{C_MUTED}{lb}{RESET}") + "  "
    lines.append(tab_row)
    lines.append(dim("─" * W))
    lines.append("")

    clipped = clip_pane(content_lines, pane_w, body_h, scroll)
    sep = f" {C_MUTED}│{RESET} "
    for i in range(body_h):
        if i < len(nav_items):
            lb = nav_items[i][1]
            lp = f"{C_SKY}{BOLD}▶ {lb}{RESET}" if i == nav_idx else f"{C_WHITE}  {lb}{RESET}"
        else:
            lp = ""
        lp = pad_vis(lp, LEFT_W)
        lines.append(lp + sep + (clipped[i] if i < len(clipped) else " " * pane_w))

    if footer is None and nav_idx < len(nav_items):
        footer = hub_hint(tab_key, nav_items[nav_idx][0])
    lines.extend(footer_line(footer or "", W))
    return lines
