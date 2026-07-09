from __future__ import annotations

from PySide6.QtCore import Property, QObject, QThread, QTimer, Signal, Slot
from PySide6.QtGui import QGuiApplication

from app.dump_load_worker import DumpLoadWorker, _apply_main_battle_progress
from controllers.common.ui_loading_bridge import ui_loading

from core.game_logic.enums import CurrencyType, TechTreeType
from core.game_logic.game_logic import GameLogic
from core.game_logic.player.player_model import PlayerModel
from controllers.collections.equipment_collection_bridge import EquipmentCollectionBridge
from controllers.forge.forge_attack_cycle_bridge import ForgeAttackCycleBridge
from controllers.profile.profile_main_bridge import ProfileMainBridge
from controllers.collections.mount_collection_bridge import MountCollectionBridge
from controllers.summon.mount_summon_test_bridge import MountSummonTestBridge
from controllers.collections.pet_collection_bridge import PetCollectionBridge
from controllers.summon.pet_egg_test_bridge import PetEggTestBridge
from controllers.summon.pet_summon_test_bridge import PetSummonTestBridge
from controllers.summon.skill_summon_test_bridge import SkillSummonTestBridge
from controllers.collections.tech_tree_collection_bridge import TechTreeCollectionBridge
from controllers.common.player_stats_bridge import PlayerStatsBridge
from controllers.common.ui_locale_bridge import register_locale_refresh
from core.format.localizer_base import clear_localization_cache
from ui.utils.ui_settings import register_display_refresh, register_economy_refresh
from utils.dump.parser import parse_dump_text
from utils.dump.to_player_model import dump_snapshot_to_player_model


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
        self._bulk_reload_depth = 0
        self._dump_load_in_progress = False
        self._dump_thread: QThread | None = None
        self._dump_worker: DumpLoadWorker | None = None
        self._dump_apply_player: PlayerModel | None = None
        self._dump_apply_step = 0
        self._deferred_summon_step = 0
        self._player_stats = PlayerStatsBridge(lambda: self._logic.player, parent=self)

        self._skill_test = SkillSummonTestBridge(self._logic, parent=self)
        self._equipment = EquipmentCollectionBridge(
            player.player_equipment_model,
            parent=self,
        )
        self._forge_attack_cycle = ForgeAttackCycleBridge(
            lambda: self._logic.player,
            parent=self,
        )
        self._profile_main = ProfileMainBridge(
            lambda: self._logic.player,
            parent=self,
        )
        self._equipment.changed.connect(self._forge_attack_cycle.refresh)
        self._equipment.changed.connect(self._profile_main.refresh)
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
            self._logic,
            tree_type=TechTreeType.Forge,
            parent=self,
        )
        self._tech_tree_power = TechTreeCollectionBridge(
            self._logic,
            tree_type=TechTreeType.Power,
            parent=self,
        )
        self._tech_tree_skills_pet_tech = TechTreeCollectionBridge(
            self._logic,
            tree_type=TechTreeType.SkillsPetTech,
            parent=self,
        )
        for tech_bridge in (
            self._tech_tree_forge,
            self._tech_tree_power,
            self._tech_tree_skills_pet_tech,
        ):
            tech_bridge.statsChanged.connect(self._on_tech_tree_stats_changed)
            tech_bridge.economyChanged.connect(self._on_tech_tree_economy_changed)
        self._tech_poll_was_researching = False
        self._tech_poll_claimable_key: tuple[tuple[int, int], ...] = ()
        self._tech_poll_timer = QTimer(self)
        self._tech_poll_timer.setInterval(1000)
        self._tech_poll_timer.timeout.connect(self._poll_tech_trees)
        self._tech_poll_timer.start()
        register_display_refresh(self._refresh_stat_displays)
        register_economy_refresh(self._on_economy_settings_changed)
        register_locale_refresh(self._on_locale_changed)
        for bridge in (
            self._skill_test,
            self._pet_summon_test,
            self._mount_summon_test,
            self._pet_egg_test,
        ):
            bridge.stateChanged.connect(self._on_action_state_changed)
        self._skill_test.statsRefreshRequested.connect(self._on_stats_refresh_requested)
        self._pet_summon_test.statsRefreshRequested.connect(self._on_stats_refresh_requested)
        self._mount_summon_test.statsRefreshRequested.connect(self._on_stats_refresh_requested)
        self._refresh_player_stats()

    def _on_stats_refresh_requested(self) -> None:
        self._refresh_player_stats()
        self._pet_collection.refresh_stat_texts()
        self._mount_collection.refresh_stat_texts()
        self._skill_test.skillCollection.refresh_stat_texts()

    def _in_bulk_reload(self) -> bool:
        return self._bulk_reload_depth > 0

    def _begin_bulk_reload(self) -> None:
        self._bulk_reload_depth += 1

    def _end_bulk_reload(self) -> None:
        self._bulk_reload_depth -= 1
        if self._bulk_reload_depth > 0:
            return
        self._refresh_player_stats()
        self.stateChanged.emit()
        QTimer.singleShot(0, self._finish_deferred_summon_refresh)

    def _finish_deferred_summon_refresh(self) -> None:
        self._deferred_summon_step = 0
        QTimer.singleShot(0, self._step_deferred_summon_refresh)

    def _step_deferred_summon_refresh(self) -> None:
        steps = (
            self._skill_test.finish_deferred_reload,
            self._pet_summon_test.finish_deferred_reload,
            self._mount_summon_test.finish_deferred_reload,
        )
        if self._deferred_summon_step < len(steps):
            steps[self._deferred_summon_step]()
            self._deferred_summon_step += 1
            QTimer.singleShot(0, self._step_deferred_summon_refresh)
            return
        self._pet_collection.set_grid_warmup_suppressed(False)
        self._mount_collection.set_grid_warmup_suppressed(False)
        self.stateChanged.emit()
        self._finish_dump_load_overlay()

    def _on_action_state_changed(self) -> None:
        if self._in_bulk_reload():
            return

    def _refresh_player_stats(self) -> None:
        self._player_stats.refresh()
        self._forge_attack_cycle.refresh()
        self._profile_main.refresh()

    def _refresh_collection_stat_displays(self) -> None:
        self._pet_collection.refresh_stat_texts()
        self._mount_collection.refresh_stat_texts()
        self._skill_test.skillCollection.refresh_stat_texts()
        self._tech_tree_forge.patch_upgrade_affordability()
        self._tech_tree_power.patch_upgrade_affordability()
        self._tech_tree_skills_pet_tech.patch_upgrade_affordability()
        self._pet_egg_test.refreshDisplayFormat()
        self.stateChanged.emit()

    def _on_economy_settings_changed(self) -> None:
        self._skill_test.stateChanged.emit()
        self._mount_summon_test.stateChanged.emit()
        self._pet_summon_test.stateChanged.emit()
        self._pet_egg_test.stateChanged.emit()
        self._tech_tree_forge.patch_upgrade_affordability()
        self._tech_tree_power.patch_upgrade_affordability()
        self._tech_tree_skills_pet_tech.patch_upgrade_affordability()
        self.stateChanged.emit()

    def _on_tech_tree_economy_changed(self) -> None:
        self._tech_tree_forge.patch_upgrade_affordability()
        self._tech_tree_power.patch_upgrade_affordability()
        self._tech_tree_skills_pet_tech.patch_upgrade_affordability()
        self.stateChanged.emit()

    def _on_tech_tree_stats_changed(self) -> None:
        self._refresh_player_stats()
        self._pet_collection.refresh_stat_texts()
        self._mount_collection.refresh_stat_texts()
        self._skill_test.skillCollection.refresh_stat_texts()
        self._pet_summon_test.predictSummon()
        self._mount_summon_test.predictSummon()
        self._tech_tree_forge.patch_upgrade_affordability()
        self._tech_tree_power.patch_upgrade_affordability()
        self._tech_tree_skills_pet_tech.patch_upgrade_affordability()

    def _poll_tech_trees(self) -> None:
        player = self._logic.player
        techtree = player.player_techtree_model
        researching = techtree.is_any_node_research_in_progress(player)

        if researching:
            self._tech_poll_was_researching = True
            for bridge in (
                self._tech_tree_forge,
                self._tech_tree_power,
                self._tech_tree_skills_pet_tech,
            ):
                bridge.tick()
            return

        has_claimable, claimable = techtree.try_get_claimable_nodes(player)
        claimable_key = tuple(sorted(claimable)) if has_claimable else ()

        need_refresh = False
        if self._tech_poll_was_researching:
            need_refresh = True
            self._tech_poll_was_researching = False
        elif claimable_key != self._tech_poll_claimable_key:
            need_refresh = True

        self._tech_poll_claimable_key = claimable_key

        if not need_refresh:
            return

        bridge_by_type = {
            TechTreeType.Forge: self._tech_tree_forge,
            TechTreeType.Power: self._tech_tree_power,
            TechTreeType.SkillsPetTech: self._tech_tree_skills_pet_tech,
        }

        if not has_claimable:
            for bridge in bridge_by_type.values():
                bridge.patch_when_research_settles()
            return

        refreshed: set[TechTreeCollectionBridge] = set()
        for tree_type, _node_id in claimable:
            bridge = bridge_by_type.get(tree_type)
            if bridge is not None and bridge not in refreshed:
                bridge.patch_when_research_settles()
                refreshed.add(bridge)

    def _refresh_stat_displays(self) -> None:
        self._refresh_player_stats()
        self._refresh_collection_stat_displays()

    def _on_locale_changed(self, _code: str) -> None:
        clear_localization_cache()

    @Property(str, notify=stateChanged)
    def lastLoadMessage(self) -> str:
        return self._last_load_message

    @Property(QObject, constant=True)
    def playerStats(self) -> PlayerStatsBridge:
        return self._player_stats

    @Property(QObject, constant=True)
    def skillTest(self) -> SkillSummonTestBridge:
        return self._skill_test

    @Property(QObject, constant=True)
    def equipment(self) -> EquipmentCollectionBridge:
        return self._equipment

    @Property(QObject, constant=True)
    def forgeAttackCycle(self) -> ForgeAttackCycleBridge:
        return self._forge_attack_cycle

    @Property(QObject, constant=True)
    def profileMain(self) -> ProfileMainBridge:
        return self._profile_main

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

    @Property(int, notify=stateChanged)
    def gemCount(self) -> int:
        return self._logic.player.player_currency_model.get(CurrencyType.Gems)

    def _dump_apply_steps(self):
        return (
            self._dump_apply_swap_player,
            self._dump_apply_skill_collection,
            self._dump_apply_pet_collection,
            self._dump_apply_mount_collection,
            self._dump_apply_summon_bridges,
            self._dump_apply_tech_tree_forge,
            self._dump_apply_tech_tree_power,
            self._dump_apply_tech_tree_skills,
            self._dump_apply_finish,
        )

    def apply_dump_text(self, text: str) -> str:
        player = dump_snapshot_to_player_model(parse_dump_text(text))
        _apply_main_battle_progress(player)
        player.player_power_model.update_power(player, publish_update=True)
        return self._apply_parsed_player_sync(player)

    def _apply_parsed_player_sync(self, player: PlayerModel) -> str:
        self._dump_apply_player = player
        for step in self._dump_apply_steps():
            step()
        return self._last_load_message

    def _apply_parsed_player_async(self, player: PlayerModel) -> None:
        self._dump_apply_player = player
        self._dump_apply_step = 0
        self._schedule_dump_apply_step()

    def _schedule_dump_apply_step(self) -> None:
        QTimer.singleShot(0, self._run_dump_apply_step)

    def _run_dump_apply_step(self) -> None:
        steps = self._dump_apply_steps()
        if self._dump_apply_step >= len(steps):
            return
        try:
            steps[self._dump_apply_step]()
        except Exception as exc:
            self._fail_dump_load(str(exc))
            return
        self._dump_apply_step += 1
        if self._dump_apply_step < len(steps):
            self._schedule_dump_apply_step()

    def _dump_apply_swap_player(self) -> None:
        player = self._dump_apply_player
        if player is None:
            raise RuntimeError("dump apply missing player")
        self._begin_bulk_reload()
        self._pet_collection.set_grid_warmup_suppressed(True)
        self._mount_collection.set_grid_warmup_suppressed(True)
        self._logic._player = player
        self._equipment.reload(player.player_equipment_model)
        self._pet_egg_test.reload_after_dump()
        self._tech_poll_was_researching = False
        self._tech_poll_claimable_key = ()

    def _dump_apply_skill_collection(self) -> None:
        player = self._dump_apply_player
        if player is None:
            return
        self._skill_test.reload_from_player(player, defer_heavy=True)

    def _dump_apply_pet_collection(self) -> None:
        player = self._dump_apply_player
        if player is None:
            return
        self._pet_collection.reload(
            player.player_pet_collection_model,
            player,
        )

    def _dump_apply_mount_collection(self) -> None:
        player = self._dump_apply_player
        if player is None:
            return
        self._mount_collection.reload(
            player.player_mount_collection_model,
            player,
        )

    def _dump_apply_summon_bridges(self) -> None:
        self._pet_summon_test.reload_after_dump(defer_heavy=True)
        self._mount_summon_test.reload_after_dump(defer_heavy=True)

    def _dump_apply_tech_tree_forge(self) -> None:
        self._tech_tree_forge.reload(self._logic)

    def _dump_apply_tech_tree_power(self) -> None:
        self._tech_tree_power.reload(self._logic)

    def _dump_apply_tech_tree_skills(self) -> None:
        self._tech_tree_skills_pet_tech.reload(self._logic)

    def _dump_apply_finish(self) -> None:
        player = self._dump_apply_player
        if player is None:
            return
        self._last_load_message = (
            f"loaded dump "
            f"(skills={self._skill_test.skillCollection.skillCount}, "
            f"pets={self._pet_collection.petCount}, "
            f"mounts={self._mount_collection.mountCount})"
        )
        print(self._last_load_message)
        self._dump_apply_player = None
        self._end_bulk_reload()

    def _begin_dump_load_overlay(self) -> None:
        loading = ui_loading()
        if loading is not None:
            loading.begin()

    def _finish_dump_load_overlay(self) -> None:
        if not self._dump_load_in_progress:
            return
        self._dump_load_in_progress = False
        loading = ui_loading()
        if loading is not None:
            loading.end()

    def _abort_bulk_reload(self) -> None:
        if self._bulk_reload_depth <= 0:
            return
        self._bulk_reload_depth = 0
        self._pet_collection.set_grid_warmup_suppressed(False)
        self._mount_collection.set_grid_warmup_suppressed(False)

    def _fail_dump_load(self, message: str) -> None:
        self._abort_bulk_reload()
        self._dump_apply_player = None
        self._last_load_message = f"load failed: {message}"
        print(self._last_load_message)
        self.stateChanged.emit()
        self._finish_dump_load_overlay()

    @Slot()
    def loadDumpFromClipboard(self) -> None:
        if self._dump_load_in_progress:
            return
        text = QGuiApplication.clipboard().text().strip()
        if not text:
            self._last_load_message = "clipboard empty"
            self.stateChanged.emit()
            return

        self._dump_load_in_progress = True
        self._begin_dump_load_overlay()
        self._last_load_message = "loading dump..."
        self.stateChanged.emit()

        self._dump_worker = DumpLoadWorker()
        self._dump_thread = QThread(self)
        self._dump_worker.moveToThread(self._dump_thread)
        self._dump_thread.started.connect(
            lambda dump_text=text: self._dump_worker.parse(dump_text)
        )
        self._dump_worker.finished.connect(self._on_dump_parsed)
        self._dump_worker.finished.connect(self._dump_thread.quit)
        self._dump_thread.finished.connect(self._cleanup_dump_thread)
        self._dump_thread.start()

    @Slot(object, str)
    def _on_dump_parsed(self, player: PlayerModel | None, error: str) -> None:
        if error or player is None:
            self._fail_dump_load(error or "parse failed")
            return
        try:
            self._apply_parsed_player_async(player)
        except Exception as exc:
            self._fail_dump_load(str(exc))
            return
        self.stateChanged.emit()

    def _cleanup_dump_thread(self) -> None:
        if self._dump_worker is not None:
            self._dump_worker.deleteLater()
            self._dump_worker = None
        self._dump_thread = None

    @Slot()
    def loadDumpFromClipboardSync(self) -> None:
        text = QGuiApplication.clipboard().text().strip()
        if not text:
            self._last_load_message = "clipboard empty"
            self.stateChanged.emit()
            return
        self._last_load_message = "loading dump..."
        self.stateChanged.emit()
        try:
            self._last_load_message = self.apply_dump_text(text)
            print(self._last_load_message)
        except Exception as exc:
            self._last_load_message = f"load failed: {exc}"
            print(self._last_load_message)
        self.stateChanged.emit()
