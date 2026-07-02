from __future__ import annotations

from collections.abc import Callable
from typing import Literal

from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt

EntryKind = Literal["pet", "egg"]


class PetCollectionEntryModel(QAbstractListModel):

    IsPetRole = Qt.ItemDataRole.UserRole + 1
    BridgeRole = Qt.ItemDataRole.UserRole + 2
    GuidRole = Qt.ItemDataRole.UserRole + 3

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._entries: list[tuple[EntryKind, QObject]] = []

    def roleNames(self) -> dict[int, bytes]:
        return {
            self.IsPetRole: b"isPet",
            self.BridgeRole: b"bridge",
            self.GuidRole: b"guid",
        }

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent.isValid():
            return 0
        return len(self._entries)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or index.row() >= len(self._entries):
            return None
        kind, bridge = self._entries[index.row()]
        if role == PetCollectionEntryModel.IsPetRole:
            return kind == "pet"
        if role == PetCollectionEntryModel.BridgeRole:
            return bridge
        if role == PetCollectionEntryModel.GuidRole:
            return getattr(bridge, "guid", "")
        return None

    def reset_entries(self, entries: list[tuple[EntryKind, QObject]]) -> None:
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def entries(self) -> list[tuple[EntryKind, QObject]]:
        return list(self._entries)

    def first_egg_bridge(self) -> QObject | None:
        for kind, bridge in self._entries:
            if kind == "egg":
                return bridge
        return None

    def pet_section_end(self) -> int:
        for index, (kind, _) in enumerate(self._entries):
            if kind == "egg":
                return index
        return len(self._entries)

    def find_egg_index(self, guid: str) -> int:
        for index, (kind, bridge) in enumerate(self._entries):
            if kind == "egg" and bridge.guid == guid:
                return index
        return -1

    def find_row_by_guid(self, guid: str) -> int:
        for index, (_, bridge) in enumerate(self._entries):
            if getattr(bridge, "guid", None) == guid:
                return index
        return -1

    def remove_row(self, index: int) -> None:
        if index < 0 or index >= len(self._entries):
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self._entries.pop(index)
        self.endRemoveRows()

    def remove_egg_by_guid(self, guid: str) -> bool:
        index = self.find_egg_index(guid)
        if index < 0:
            return False
        self.remove_row(index)
        return True

    def insert_entry(self, index: int, kind: EntryKind, bridge: QObject) -> None:
        index = max(0, min(index, len(self._entries)))
        self.beginInsertRows(QModelIndex(), index, index)
        self._entries.insert(index, (kind, bridge))
        self.endInsertRows()

    def insert_sorted(
        self,
        kind: EntryKind,
        bridge: QObject,
        sort_key: Callable[[QObject], tuple],
    ) -> None:
        index = self._find_insert_index(kind, bridge, sort_key)
        self.insert_entry(index, kind, bridge)

    def _find_insert_index(
        self,
        kind: EntryKind,
        bridge: QObject,
        sort_key: Callable[[QObject], tuple],
    ) -> int:
        key = sort_key(bridge)
        if kind == "pet":
            for index, (entry_kind, entry_bridge) in enumerate(self._entries):
                if entry_kind == "egg":
                    return index
                if sort_key(entry_bridge) > key:
                    return index
            return self.pet_section_end()
        pet_end = self.pet_section_end()
        for index in range(pet_end, len(self._entries)):
            _, entry_bridge = self._entries[index]
            if sort_key(entry_bridge) > key:
                return index
        return len(self._entries)
