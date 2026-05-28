# ui/views/collection/footer_sync.py — duck-typed hatch footer hooks (no HatchBarDiv import)
from __future__ import annotations

from typing import Any, Protocol

from ui.services.collection_selection import CollectionSelection


class HatchFooter(Protocol):
    def sync_panel_width(self, panel_inner_width: int) -> None: ...
    @property
    def row(self) -> Any: ...


def as_hatch_footer(footer: object | None) -> HatchFooter | None:
    if footer is None:
        return None
    if hasattr(footer, "sync_panel_width") and hasattr(footer, "row"):
        return footer  # type: ignore[return-value]
    hatch = getattr(footer, "hatch_bar", None)
    if hatch is not None and hasattr(hatch, "sync_panel_width") and hasattr(hatch, "row"):
        return hatch  # type: ignore[return-value]
    return None


def sync_hatch_footer(
    footer: HatchFooter | None,
    panel_width: int,
    *,
    grid_margin_h: int | None = None,
) -> None:
    if footer is None:
        return
    if grid_margin_h is not None and hasattr(footer, "sync_panel_width"):
        footer.sync_panel_width(panel_width, grid_margin_h=grid_margin_h)
    else:
        footer.sync_panel_width(panel_width)


def refresh_hatch_footer(
    footer: HatchFooter | None,
    slots: list,
    selection: CollectionSelection | None,
) -> None:
    if footer is None:
        return
    row = footer.row
    if hasattr(row, "set_slots"):
        row.set_slots(slots)
    if hasattr(row, "set_selected"):
        row.set_selected(selection)
