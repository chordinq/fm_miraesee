from PySide6.QtCore import QObject, Property, Signal

from core.game_logic.enums import AscensionLevel
from core.game_logic.player.player_skill_collection_model import PlayerSkillCollectionModel
from localizer import ascension_loc_from_level
from skill_model_bridge import SkillModelBridge


class SkillCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerSkillCollectionModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._refresh_bridges()

    def _refresh_bridges(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)
        self._skill_bridges: list[SkillModelBridge] = [
            SkillModelBridge(skill, parent=self)
            for skill in self._collection.get_player_skills()
        ]

    def refresh(self) -> None:
        self._refresh_bridges()
        self.changed.emit()

    @Property(int, notify=changed)
    def ascensionLevel(self) -> int:
        return self._ascension_level

    @Property(str, notify=changed)
    def ascensionLocId(self) -> str:
        return self._ascension_loc_id

    @Property(str, notify=changed)
    def ascensionLocTable(self) -> str:
        return self._ascension_loc_table

    @Property("QVariantList", notify=changed)
    def skills(self) -> list[SkillModelBridge]:
        return self._skill_bridges

    @Property(int, notify=changed)
    def skillCount(self) -> int:
        return len(self._skill_bridges)
