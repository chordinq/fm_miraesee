from __future__ import annotations


def display_name(name: str) -> str:
    return name.replace(" ", "") if name else name
