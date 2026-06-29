from __future__ import annotations

from types import SimpleNamespace

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication

from core.game_logic.enums import CurrencyType, TechTreeType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from controllers.collections.equipment_collection_bridge import EquipmentCollectionBridge
from controllers.collections.mount_collection_bridge import MountCollectionBridge
from controllers.summon.mount_summon_test_bridge import MountSummonTestBridge
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.summon.pet_egg_test_bridge import PetEggTestBridge
from controllers.summon.pet_summon_test_bridge import PetSummonTestBridge
from controllers.summon.skill_summon_test_bridge import SkillSummonTestBridge
from controllers.collections.tech_tree_collection_bridge import TechTreeCollectionBridge
from ui.utils.ui_settings import register_display_refresh
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


def _apply_main_battle_progress(player: PlayerModel) -> None:
    player.main_battle_progress = SimpleNamespace(
        difficulty_idx=0,
        age_idx=99,
        battle_idx=0,
    )


def _empty_player() -> PlayerModel:
    player = dump_snapshot_to_player_model(parse_dump_text(""))
    _apply_main_battle_progress(player)
    return player


class GameTestSessionBridge(QObject):
    stateChanged = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        super().__init__(parent)
        player = _empty_player()
        self._logic = GameLogic(player)
        self._last_load_message = ""

        self._skill_test = SkillSummonTestBridge(self._logic, parent=self)
        self._equipment = EquipmentCollectionBridge(
            player.player_equipment_model,
            parent=self,
        )
        self._pet_collection = PetCollectionBridge(
            player.player_pet_collection_model,
            player,
            parent=self,
        )
        self._pet_egg_test = PetEggTestBridge(
            self._logic,
            self._pet_collection,
            parent=self,
        )
        self._pet_summon_test = PetSummonTestBridge(
            self._logic,
            self._pet_collection,
            parent=self,
        )
        self._mount_collection = MountCollectionBridge(
            player.player_mount_collection_model,
            player,
            parent=self,
        )
        self._mount_summon_test = MountSummonTestBridge(
            self._logic,
            self._mount_collection,
            parent=self,
        )
        self._tech_tree_forge = TechTreeCollectionBridge(
            player,
            tree_type=TechTreeType.Forge,
            parent=self,
        )
        self._tech_tree_power = TechTreeCollectionBridge(
            player,
            tree_type=TechTreeType.Power,
            parent=self,
        )
        self._tech_tree_skills_pet_tech = TechTreeCollectionBridge(
            player,
            tree_type=TechTreeType.SkillsPetTech,
            parent=self,
        )
        for tech_bridge in (
            self._tech_tree_forge,
            self._tech_tree_power,
            self._tech_tree_skills_pet_tech,
        ):
            tech_bridge.statsChanged.connect(self._on_tech_tree_stats_changed)
        self._tech_poll_timer = QTimer(self)
        self._tech_poll_timer.setInterval(1000)
        self._tech_poll_timer.timeout.connect(self._poll_tech_trees)
        self._tech_poll_timer.start()
        register_display_refresh(self._refresh_stat_displays)

    def _on_tech_tree_stats_changed(self) -> None:
        self._skill_test.stateChanged.emit()
        self._mount_summon_test.stateChanged.emit()
        self._pet_summon_test.stateChanged.emit()
        self._pet_egg_test.stateChanged.emit()
        self._pet_collection.refresh()
        self._mount_collection.refresh()
        self.stateChanged.emit()

    def _poll_tech_trees(self) -> None:
        player = self._logic.player
        techtree = player.player_techtree_model
        if techtree.is_any_node_research_in_progress(player):
            pass
        else:
            has_claimable, _ = techtree.try_get_claimable_nodes(player)
            if not has_claimable:
                return
        self._tech_tree_forge.refresh()
        self._tech_tree_power.refresh()
        self._tech_tree_skills_pet_tech.refresh()

    def _refresh_stat_displays(self) -> None:
        self._pet_collection.refresh()
        self._mount_collection.refresh()
        self._skill_test.skillCollection.refresh()
        self._tech_tree_forge.refresh()
        self._tech_tree_power.refresh()
        self._tech_tree_skills_pet_tech.refresh()
        self._pet_egg_test.refreshDisplayFormat()
        self.stateChanged.emit()

    @Property(str, notify=stateChanged)
    def lastLoadMessage(self) -> str:
        return self._last_load_message

    @Property(QObject, constant=True)
    def skillTest(self) -> SkillSummonTestBridge:
        return self._skill_test

    @Property(QObject, constant=True)
    def equipment(self) -> EquipmentCollectionBridge:
        return self._equipment

    @Property(QObject, constant=True)
    def petCollection(self) -> PetCollectionBridge:
        return self._pet_collection

    @Property(QObject, constant=True)
    def petEggTest(self) -> PetEggTestBridge:
        return self._pet_egg_test

    @Property(QObject, constant=True)
    def petSummonTest(self) -> PetSummonTestBridge:
        return self._pet_summon_test

    @Property(QObject, constant=True)
    def mountCollection(self) -> MountCollectionBridge:
        return self._mount_collection

    @Property(QObject, constant=True)
    def mountSummonTest(self) -> MountSummonTestBridge:
        return self._mount_summon_test

    @Property(QObject, constant=True)
    def techTreeForge(self) -> TechTreeCollectionBridge:
        return self._tech_tree_forge

    @Property(QObject, constant=True)
    def techTreePower(self) -> TechTreeCollectionBridge:
        return self._tech_tree_power

    @Property(QObject, constant=True)
    def techTreeSkillsPetTech(self) -> TechTreeCollectionBridge:
        return self._tech_tree_skills_pet_tech

    @Property(int, notify=stateChanged)
    def techPotionCount(self) -> int:
        return self._logic.player.player_currency_model.get(CurrencyType.TechPotions)

    def apply_dump_text(self, text: str) -> str:
        player = dump_snapshot_to_player_model(parse_dump_text(text))
        _apply_main_battle_progress(player)
        self._logic._player = player

        self._skill_test.reload_from_player(player)
        self._equipment.reload(player.player_equipment_model)
        self._pet_collection.reload(
            player.player_pet_collection_model,
            player,
        )
        self._pet_egg_test.reload_after_dump()
        self._pet_summon_test.reload_after_dump()
        self._mount_collection.reload(
            player.player_mount_collection_model,
            player,
        )
        self._mount_summon_test.reload_after_dump()
        self._tech_tree_forge.reload(player)
        self._tech_tree_power.reload(player)
        self._tech_tree_skills_pet_tech.reload(player)

        return (
            f"loaded dump "
            f"(skills={self._skill_test.skillCollection.skillCount}, "
            f"pets={self._pet_collection.petCount}, "
            f"mounts={self._mount_collection.mountCount})"
        )

    @Slot()
    def loadDumpFromClipboard(self) -> None:
        text = QGuiApplication.clipboard().text().strip()
        if not text:
            self._last_load_message = "clipboard empty"
            self.stateChanged.emit()
            return
        try:
            self._last_load_message = self.apply_dump_text(text)
            print(self._last_load_message)
        except Exception as exc:
            self._last_load_message = f"load failed: {exc}"
            print(self._last_load_message)
        self.stateChanged.emit()
