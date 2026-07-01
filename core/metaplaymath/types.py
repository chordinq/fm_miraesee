from __future__ import annotations

from typing import NewType

"""Canonical raw storage types for Metaplay fixed-point math (zero runtime cost)."""

F64Raw = NewType("F64Raw", int)
FD6Raw = NewType("FD6Raw", int)
