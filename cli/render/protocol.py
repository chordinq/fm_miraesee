# cli/render/protocol.py
"""Renderer protocols — implement these to swap text / Pillow / etc."""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class LineRenderer(Protocol):
    """Returns lines of ANSI text (no printing)."""

    def render(self, session) -> list[str]:
        ...


@runtime_checkable
class EquipmentRenderer(Protocol):
    """Forge equipped gear. Default: text lines; swap for Pillow image export."""

    def render(self, session) -> list[str]:
        ...
