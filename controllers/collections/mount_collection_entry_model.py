from __future__ import annotations

from PySide6.QtCore import QAbstractListModel, QModelIndex, QObject, Qt


class MountCollectionEntryModel(QAbstractListModel):

    BridgeRole = Qt.ItemDataRole.UserRole + 1
    GuidRole = Qt.ItemDataRole.UserRole + 2

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._entries: list[QObject] = []

    def roleNames(self) -> dict[int, bytes]:
        return {
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
        bridge = self._entries[index.row()]
        if role == MountCollectionEntryModel.BridgeRole:
            return bridge
        if role == MountCollectionEntryModel.GuidRole:
            return getattr(bridge, "guid", "")
        return None

    def reset_entries(self, entries: list[QObject]) -> None:
        self.beginResetModel()
        self._entries = list(entries)
        self.endResetModel()

    def entries(self) -> list[QObject]:
        return list(self._entries)

    def find_row_by_guid(self, guid: str) -> int:
        for index, bridge in enumerate(self._entries):
            if getattr(bridge, "guid", None) == guid:
                return index
        return -1

    def remove_row(self, index: int) -> None:
        if index < 0 or index >= len(self._entries):
            return
        self.beginRemoveRows(QModelIndex(), index, index)
        self._entries.pop(index)
        self.endRemoveRows()

    def insert_entry(self, index: int, bridge: QObject) -> None:
        index = max(0, min(index, len(self._entries)))
        self.beginInsertRows(QModelIndex(), index, index)
        self._entries.insert(index, bridge)
        self.endInsertRows()
