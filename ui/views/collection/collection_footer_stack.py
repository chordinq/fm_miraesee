# ui/views/collection/collection_footer_stack.py — hatch + summon footers in one panel slot
from __future__ import annotations

from PySide6.QtWidgets import QVBoxLayout, QWidget


class CollectionFooterStack(QWidget):
    """Vertical stack of panel footers; exposes hatch bar API for CollectionScreenDiv."""

    def __init__(self, *widgets: QWidget, spacing: int = 0) -> None:
        super().__init__()
        self.setObjectName("CollectionFooterStack")
        self.setStyleSheet("background: transparent;")
        self._widgets = list(widgets)
        self._hatch_bar = _find_hatch_bar(self._widgets)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(spacing)
        for w in self._widgets:
            layout.addWidget(w, 0)

    @property
    def hatch_bar(self) -> QWidget | None:
        return self._hatch_bar

    @property
    def row(self):
        if self._hatch_bar is None:
            raise AttributeError("CollectionFooterStack has no hatch bar child")
        return self._hatch_bar.row

    def sync_panel_width(self, panel_width: int, **kwargs) -> None:
        for w in self._widgets:
            if not hasattr(w, "sync_panel_width"):
                continue
            try:
                w.sync_panel_width(panel_width, **kwargs)
            except TypeError:
                w.sync_panel_width(panel_width)


def _find_hatch_bar(widgets: list[QWidget]) -> QWidget | None:
    for w in widgets:
        if hasattr(w, "row") and hasattr(w, "sync_panel_width"):
            return w
    return None


def stack_panel_footers(*widgets: QWidget, spacing: int = 0) -> CollectionFooterStack:
    return CollectionFooterStack(*widgets, spacing=spacing)
