from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Property, Signal, Slot

from core.game_logic.enums import AscensionLevel

if TYPE_CHECKING:
	from core.game_logic.actions.summon.skill_summon_action import SummonedSkillInfo
from core.game_logic.player.player_model import PlayerModel
from core.game_logic.player.player_skill_collection_model import PlayerSkillCollectionModel
from ui.utils.localizer import ascension_loc_from_level
from ui.utils.rarity_counts import count_rarities
from controllers.models.skill_model_bridge import SkillModelBridge


class SkillCollectionBridge(QObject):

    changed = Signal()

    def __init__(
        self,
        collection: PlayerSkillCollectionModel,
        player: PlayerModel,
        parent: QObject | None = None,
    ) -> None:
        super().__init__(parent)
        self._collection = collection
        self._player = player
        self._skill_bridge_by_type: dict[int, SkillModelBridge] = {}
        self._skill_bridges: list[SkillModelBridge] = []
        self._sync_ascension()
        self._sync_skill_bridges()

    def _discard_bridge(self, bridge: QObject) -> None:
        bridge.setParent(None)
        bridge.deleteLater()

    def _clear_bridge_cache(self) -> None:
        for bridge in self._skill_bridge_by_type.values():
            self._discard_bridge(bridge)
        self._skill_bridge_by_type.clear()
        self._skill_bridges = []

    def _sync_ascension(self) -> None:
        ascension_level = AscensionLevel(self._collection.ascension_model.current_level)
        self._ascension_level = int(ascension_level.value)
        self._ascension_loc_id, self._ascension_loc_table = ascension_loc_from_level(ascension_level)

    def _sync_skill_bridges(self) -> None:
        skills = self._collection.get_player_skills()
        active_types = {int(skill.type.value) for skill in skills}
        for skill_type in list(self._skill_bridge_by_type):
            if skill_type not in active_types:
                self._discard_bridge(self._skill_bridge_by_type.pop(skill_type))

        ordered: list[SkillModelBridge] = []
        for skill in skills:
            skill_type = int(skill.type.value)
            bridge = self._skill_bridge_by_type.get(skill_type)
            if bridge is None:
                bridge = SkillModelBridge(skill, self._player, parent=self)
                self._skill_bridge_by_type[skill_type] = bridge
            else:
                bridge.sync()
            ordered.append(bridge)
        self._skill_bridges = ordered
        self._rarity_counts = count_rarities(
            self._skill_bridges,
            lambda bridge: bridge._rarity,
        )

    def reload(
        self,
        collection: PlayerSkillCollectionModel,
        player: PlayerModel,
    ) -> None:
        self._collection = collection
        self._player = player
        self._clear_bridge_cache()
        self._sync_ascension()
        self._sync_skill_bridges()
        self.changed.emit()

    @Slot(str)
    def setUiLanguage(self, language: str) -> None:
        self.refresh_stat_texts()

    def refresh_stat_texts(self) -> None:
        for bridge in self._skill_bridge_by_type.values():
            bridge.refresh_localized()

    def refresh(self) -> None:
        self._sync_ascension()
        self._sync_skill_bridges()
        self.changed.emit()

    def patch_after_skill_summon(self, summoned: list[SummonedSkillInfo]) -> None:
        for info in summoned:
            skill = self._collection.try_get_skill(info.type)
            if skill is None:
                continue
            skill_type = int(skill.type.value)
            bridge = self._skill_bridge_by_type.get(skill_type)
            if bridge is None:
                bridge = SkillModelBridge(skill, self._player, parent=self)
                self._skill_bridge_by_type[skill_type] = bridge
            else:
                bridge.sync()
        self._skill_bridges = [
            self._skill_bridge_by_type[int(skill.type.value)]
            for skill in self._collection.get_player_skills()
            if int(skill.type.value) in self._skill_bridge_by_type
        ]
        self._rarity_counts = count_rarities(
            self._skill_bridges,
            lambda bridge: bridge._rarity,
        )
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

    @Property("QVariantList", notify=changed)
    def rarityCounts(self) -> list[dict[str, int]]:
        return self._rarity_counts
