from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_skill_collection_model import PlayerSkillCollectionModel
from skill_model_bridge import SkillModelBridge


class SkillCollectionBridge(QObject):
    """Read-only QML bridge for PlayerSkillCollectionModel."""

    changed = Signal()

    def __init__(
        self,
        collection: PlayerSkillCollectionModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        ascension_level = AscensionLevel(collection.ascension_model.current_level)
        self._skill_bridges: list[SkillModelBridge] = [
            SkillModelBridge(skill, ascension_level=ascension_level, parent=self)
            for skill in collection.to_list()
        ]

    @Property("QVariantList", notify=changed)
    def skills(self) -> list[SkillModelBridge]:
        return self._skill_bridges

    @Property(int, notify=changed)
    def skillCount(self) -> int:
        return len(self._skill_bridges)
